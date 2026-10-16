
from fastapi import Body, FastAPI, HTTPException
from fastapi.responses import JSONResponse, RedirectResponse

from . import cache, db
from .codes import (
    ALPHABET,
    LinkError,
    encode,
    is_safe,
    normalise_url,
    validate_custom,
)

app = FastAPI(title="url-shortener")


def encode_link_id(link_id: int) -> str:
    """Encode a database ID as a unique short code of at least 3 characters.

    Prefixing the normal encoding with the alphabet's first character keeps
    the original encoding as a suffix and avoids changing the ID itself.
    """
    code = encode(link_id)
    if len(code) < 3:
        code = ALPHABET[0] * (3 - len(code)) + code
    return code


@app.get("/health")
def health():
    out = {"status": "ok", "postgres": False, "redis": False}

    try:
        db.query("SELECT 1")
        out["postgres"] = True
    except Exception as e:
        out["pg_error"] = str(e)

    try:
        cache.client().ping()
        out["redis"] = True
    except Exception as e:
        out["redis_error"] = str(e)

    if out["postgres"] and out["redis"]:
        return out

    return JSONResponse(out, status_code=503)


@app.post("/shorten", status_code=201)
def shorten(payload: dict = Body(...)):
    try:
        url = normalise_url(payload.get("url"))
    except LinkError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not is_safe(url):
        raise HTTPException(
            status_code=400,
            detail="that host is not allowed",
        )

    custom = payload.get("custom")

    if custom:
        try:
            code = validate_custom(custom)
        except LinkError as e:
            raise HTTPException(status_code=400, detail=str(e))

        if db.one("SELECT 1 FROM links WHERE code = %s", (code,)):
            raise HTTPException(
                status_code=409,
                detail=f"{code!r} is already taken",
            )

        row = db.one(
            "INSERT INTO links (code, url) VALUES (%s, %s) "
            "RETURNING id, code",
            (code, url),
        )
        code = row["code"]

    else:
        # Insert an empty code to obtain a database-generated unique ID.
        row = db.one(
            "INSERT INTO links (code, url) VALUES ('', %s) RETURNING id",
            (url,),
        )
        code = encode_link_id(row["id"])

        db.query(
            "UPDATE links SET code = %s WHERE id = %s",
            (code, row["id"]),
            fetch=False,
        )

    cache.drop(f"link:{code}")

    return {
        "code": code,
        "url": url,
        "short": f"/{code}",
    }


@app.get("/api/links")
def list_links():
    links = db.query(
        "SELECT l.code, l.url, l.created_at, "
        "(SELECT count(*) FROM clicks c WHERE c.link_id = l.id) AS clicks "
        "FROM links l "
        "WHERE l.code <> '' "
        "ORDER BY l.id DESC LIMIT 200"
    )
    return {"links": links}


@app.get("/api/links/{code}/stats")
def stats(code: str):
    link = db.one(
        "SELECT id, code, url FROM links WHERE code = %s",
        (code,),
    )

    if not link:
        raise HTTPException(status_code=404, detail="no such code")

    return {
        "code": code,
        "url": link["url"],
        "per_day": db.query(
            "SELECT clicked_at::date AS day, count(*) AS clicks "
            "FROM clicks WHERE link_id = %s "
            "GROUP BY day ORDER BY day DESC LIMIT 30",
            (link["id"],),
        ),
        "referrers": db.query(
            "SELECT coalesce(nullif(referrer, ''), '(direct)') AS referrer, "
            "count(*) AS clicks FROM clicks "
            "WHERE link_id = %s "
            "GROUP BY 1 ORDER BY clicks DESC LIMIT 10",
            (link["id"],),
        ),
    }


@app.get("/{code}")
def follow(code: str):
    """Redirect to the destination and record the click."""
    hit = cache.get_json(f"link:{code}")

    if hit:
        link_id, url = hit["id"], hit["url"]
    else:
        link = db.one(
            "SELECT id, url FROM links WHERE code = %s",
            (code,),
        )

        if not link:
            raise HTTPException(status_code=404, detail="no such code")

        link_id, url = link["id"], link["url"]

        cache.set_json(
            f"link:{code}",
            {"id": link_id, "url": url},
            ttl=3600,
        )

    db.query(
        "INSERT INTO clicks (link_id, referrer) VALUES (%s, %s)",
        (link_id, ""),
        fetch=False,
    )

    cache.client().incr(f"clicks:{code}")

    return RedirectResponse(url, status_code=302)
