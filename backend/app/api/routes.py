"""API routes."""

from fastapi import APIRouter, HTTPException, Query

from app.core.cache import cache_ok
from app.core.config import get_settings
from app.schemas.portfolio import AnalyzeRequest, AnalyzeResponse, BenchmarkStats, HealthResponse
from app.services.analyze import analyze_portfolio
from app.services.benchmarks import get_benchmark_stats
from app.services.market_data import MarketDataError

router = APIRouter(prefix="/api/v1")


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    ok = cache_ok()
    return HealthResponse(status="ok" if ok else "degraded", cache_ok=ok, app=settings.app_name)


@router.post("/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return analyze_portfolio(req)
    except MarketDataError as exc:
        raise HTTPException(status_code=400, detail={"code": "market_data", "message": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "upstream", "message": f"Analysis failed: {exc}"},
        ) from exc


@router.get("/benchmarks/{sector}", response_model=BenchmarkStats)
def benchmarks(
    sector: str,
    lookback_years: int = Query(default=2, ge=1, le=3),
) -> BenchmarkStats:
    try:
        data = get_benchmark_stats(sector, lookback_years)
        return BenchmarkStats(**data)
    except MarketDataError as exc:
        raise HTTPException(status_code=400, detail={"code": "market_data", "message": str(exc)}) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={"code": "upstream", "message": str(exc)},
        ) from exc
