"""Dashboard summary response schema."""
from typing import Optional
from pydantic import BaseModel, Field


class SummaryResponse(BaseModel):
    total_violations: Optional[int] = Field(None, description="Total parking violation records")
    total_spatial_cells: Optional[int] = Field(None, description="Unique spatial grid cells")
    # Stability classes matching actual CSV values: Persistent, Volatile, Declining, Emerging
    persistent_hotspots: Optional[int] = Field(None, description="Cells with stability_class=Persistent")
    volatile_hotspots: Optional[int] = Field(None, description="Cells with stability_class=Volatile")
    declining_hotspots: Optional[int] = Field(None, description="Cells with stability_class=Declining")
    emerging_hotspots: Optional[int] = Field(None, description="Cells with stability_class=Emerging")
    # Risk categories matching actual CSV values: CRITICAL, HIGH, MODERATE, LOW
    critical_risk_zones: Optional[int] = Field(None, description="Cells with congestion_risk_category=CRITICAL")
    high_risk_zones: Optional[int] = Field(None, description="Cells with congestion_risk_category=HIGH")
    moderate_risk_zones: Optional[int] = Field(None, description="Cells with congestion_risk_category=MODERATE")
    low_risk_zones: Optional[int] = Field(None, description="Cells with congestion_risk_category=LOW")
    best_model_name: Optional[str] = Field(None, description="Top model/ensemble from V2 evaluation")
    best_recall_at_20: Optional[float] = Field(None, description="Best Recall@20 (V2: LightGBM=0.775)")
    best_recall_at_50: Optional[float] = Field(None, description="Best Recall@50 (V2: EnsH=0.82)")
    top_police_station: Optional[str] = Field(None, description="Station with highest case volume")
    top_junction: Optional[str] = Field(None, description="Junction with highest case volume")
    april_normalization_factor: Optional[float] = Field(
        None, description="Median factor applied to April counts (30/8 = 3.75)"
    )
    total_patrol_cells: Optional[int] = Field(None, description="Cells in enhanced patrol table")
    top20_patrol_cells: Optional[int] = Field(None, description="Cells in top-20 patrol list")
