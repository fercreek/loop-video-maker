"""
core/db.py — SQLite history database for Loop Video Maker.

Tracks every generated image, audio file, and video with metadata.
Schema is stable; migrations add columns if needed.

Usage:
    from core.db import init_db, record_image, record_audio, record_video, get_images
    init_db()
    image_id = record_image(path="output/imagen_20260403.jpg", style="Cielo nocturno",
                             prompt="", theme="paz")
"""
from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from contextlib import contextmanager
from typing import Optional

# Default DB path — relative to project root
_DEFAULT_DB = os.path.join(os.path.dirname(__file__), "..", "data", "history.db")
_db_path: str = os.path.abspath(_DEFAULT_DB)


def init_db(db_path: Optional[str] = None) -> None:
    """
    Initialize the database and create tables if they don't exist.
    Call once at app startup. Safe to call multiple times.
    """
    global _db_path
    if db_path:
        _db_path = os.path.abspath(db_path)
    os.makedirs(os.path.dirname(_db_path), exist_ok=True)
    with _connect() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS images (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                path        TEXT    NOT NULL,
                style       TEXT,
                prompt      TEXT    DEFAULT '',
                theme       TEXT    DEFAULT '',
                width       INTEGER DEFAULT 1920,
                height      INTEGER DEFAULT 1080,
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS audio (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                path         TEXT    NOT NULL,
                mood         TEXT    DEFAULT '',
                duration_sec INTEGER DEFAULT 0,
                generator    TEXT    DEFAULT 'ambient',
                created_at   TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS videos (
                id                INTEGER PRIMARY KEY AUTOINCREMENT,
                path              TEXT    NOT NULL,
                theme             TEXT    DEFAULT '',
                duration_min      INTEGER DEFAULT 0,
                seconds_per_verse INTEGER DEFAULT 12,
                image_id          INTEGER REFERENCES images(id),
                audio_id          INTEGER REFERENCES audio(id),
                efecto_imagen     TEXT    DEFAULT '',
                verses_count      INTEGER DEFAULT 0,
                created_at        TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS batch_jobs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                theme       TEXT    DEFAULT '',
                formats     TEXT    DEFAULT '',
                total_items INTEGER DEFAULT 0,
                completed   INTEGER DEFAULT 0,
                status      TEXT    DEFAULT 'pending',
                created_at  TEXT    NOT NULL
            );

            CREATE TABLE IF NOT EXISTS posts (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                path         TEXT    NOT NULL,
                format_key   TEXT    DEFAULT 'post_1080',
                theme        TEXT    DEFAULT '',
                verse_ref    TEXT    DEFAULT '',
                caption_path TEXT    DEFAULT '',
                batch_id     INTEGER REFERENCES batch_jobs(id),
                image_id     INTEGER REFERENCES images(id),
                width        INTEGER DEFAULT 1080,
                height       INTEGER DEFAULT 1080,
                created_at   TEXT    NOT NULL
            );
        """)

        # Add new columns to videos table (idempotent)
        for col_sql in [
            "ALTER TABLE videos ADD COLUMN format_key TEXT DEFAULT 'youtube_1080'",
            "ALTER TABLE videos ADD COLUMN batch_id INTEGER REFERENCES batch_jobs(id)",
        ]:
            try:
                conn.execute(col_sql)
            except sqlite3.OperationalError:
                pass  # Column already exists


@contextmanager
def _connect():
    conn = sqlite3.connect(_db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Write helpers ───────────────────────────────────────────────

def record_image(
    path: str,
    style: str = "",
    prompt: str = "",
    theme: str = "",
    width: int = 1920,
    height: int = 1080,
) -> int:
    """Insert an image record. Returns the new row id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO images (path, style, prompt, theme, width, height, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (os.path.abspath(path), style, prompt, theme, width, height, _now()),
        )
        return cur.lastrowid


def record_audio(
    path: str,
    mood: str = "",
    duration_sec: int = 0,
    generator: str = "ambient",
) -> int:
    """Insert an audio record. Returns the new row id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO audio (path, mood, duration_sec, generator, created_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (os.path.abspath(path), mood, duration_sec, generator, _now()),
        )
        return cur.lastrowid


def record_video(
    path: str,
    theme: str = "",
    duration_min: int = 0,
    seconds_per_verse: int = 12,
    image_id: Optional[int] = None,
    audio_id: Optional[int] = None,
    efecto_imagen: str = "",
    verses_count: int = 0,
) -> int:
    """Insert a video record. Returns the new row id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO videos "
            "(path, theme, duration_min, seconds_per_verse, image_id, audio_id, "
            " efecto_imagen, verses_count, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                os.path.abspath(path), theme, duration_min, seconds_per_verse,
                image_id, audio_id, efecto_imagen, verses_count, _now(),
            ),
        )
        return cur.lastrowid


# ─── Read helpers ────────────────────────────────────────────────

def get_images(limit: int = 50) -> list[dict]:
    """Return newest images first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM images ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_audio(limit: int = 20) -> list[dict]:
    """Return newest audio records first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM audio ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_videos(limit: int = 20) -> list[dict]:
    """Return newest videos first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM videos ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_last_image_id() -> Optional[int]:
    """Returns the id of the most recently recorded image, or None."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM images ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row["id"] if row else None


def get_last_audio_id() -> Optional[int]:
    """Returns the id of the most recently recorded audio, or None."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT id FROM audio ORDER BY id DESC LIMIT 1"
        ).fetchone()
    return row["id"] if row else None


# ─── Batch & post helpers ─────────────────────────────────────────

def record_batch_job(
    theme: str = "",
    formats: str = "",
    total_items: int = 0,
) -> int:
    """Create a new batch job record. Returns the new row id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO batch_jobs (theme, formats, total_items, completed, status, created_at) "
            "VALUES (?, ?, ?, 0, 'running', ?)",
            (theme, formats, total_items, _now()),
        )
        return cur.lastrowid


def update_batch_progress(batch_id: int, completed: int, status: str = "running") -> None:
    """Update batch job progress."""
    with _connect() as conn:
        conn.execute(
            "UPDATE batch_jobs SET completed = ?, status = ? WHERE id = ?",
            (completed, status, batch_id),
        )


def record_post(
    path: str,
    format_key: str = "post_1080",
    theme: str = "",
    verse_ref: str = "",
    caption_path: str = "",
    batch_id: Optional[int] = None,
    image_id: Optional[int] = None,
    width: int = 1080,
    height: int = 1080,
) -> int:
    """Insert a post record. Returns the new row id."""
    with _connect() as conn:
        cur = conn.execute(
            "INSERT INTO posts "
            "(path, format_key, theme, verse_ref, caption_path, batch_id, image_id, "
            " width, height, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                os.path.abspath(path), format_key, theme, verse_ref,
                caption_path, batch_id, image_id, width, height, _now(),
            ),
        )
        return cur.lastrowid


def get_posts(limit: int = 50) -> list[dict]:
    """Return newest posts first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM posts ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_batch_jobs(limit: int = 20) -> list[dict]:
    """Return newest batch jobs first."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT * FROM batch_jobs ORDER BY id DESC LIMIT ?", (limit,)
        ).fetchall()
    return [dict(r) for r in rows]
