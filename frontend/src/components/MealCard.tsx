import { useMemo } from "react";
import { useAuth } from "../features/auth/context/AuthContext";
import { Button } from "./ui/Button";
import { Badge } from "./ui/Badge";
import { Card } from "./ui/Card";
import type { MealCardItem } from "../types/api";

interface MealCardProps {
  meal: MealCardItem;
  onRequestSwap?: (meal: MealCardItem) => void;
}

export function MealCard({ meal, onRequestSwap }: MealCardProps) {
  const { user } = useAuth();
  const isOwnMeal = user?.id === meal.owner_id;

  const tags = useMemo(() => meal.dietary_tags.length ? meal.dietary_tags.join(" · ") : "No tags", [meal.dietary_tags]);

  return (
    <Card style={{ display: "grid", gap: "1rem", overflow: "hidden", borderRadius: "1.5rem", background: "#fff", border: "1px solid #f1ddd0" }}>
      <div style={{ position: "relative", minHeight: "13rem", background: "#f8f3ec", display: "grid", placeItems: "center", overflow: "hidden" }}>
        {meal.image_url ? (
          <img
            src={meal.image_url}
            alt={meal.title}
            style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center" }}
          />
        ) : (
          <div style={{ color: "#64726c", fontWeight: 700 }}>No meal image</div>
        )}
        <Badge
          style={{
            position: "absolute",
            top: "1rem",
            right: "1rem",
            background: meal.compatibility_score > 75 ? "#d8f1dc" : meal.compatibility_score >= 50 ? "#fef9c3" : "#fee2e2",
            color: meal.compatibility_score > 75 ? "#166534" : meal.compatibility_score >= 50 ? "#92400e" : "#991b1b",
          }}
        >
          {meal.compatibility_score}%
        </Badge>
      </div>

      <div style={{ display: "grid", gap: "0.85rem", padding: "1rem 1rem 1.25rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "flex-start", flexWrap: "wrap" }}>
          <div>
            <h3 style={{ margin: 0, fontSize: "1.15rem" }}>{meal.title}</h3>
            <p style={{ margin: "0.45rem 0 0", color: "#5b6b63" }}>{meal.cuisine} · {tags}</p>
            {meal.owner_name ? <p style={{ margin: "0.35rem 0 0", color: "#64726c", fontSize: "0.95rem" }}>By {meal.owner_name}</p> : null}
          </div>
        </div>

        <p style={{ margin: 0, color: "#405048" }}>{meal.description}</p>

        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", color: "#64726c", fontSize: "0.92rem" }}>
          <span>{meal.distance_km.toFixed(1)} km away</span>
          {meal.location ? (
            <span>Meet at {meal.location}</span>
          ) : meal.latitude != null && meal.longitude != null ? (
            <span>Meet at {meal.latitude.toFixed(4)}, {meal.longitude.toFixed(4)}</span>
          ) : null}
          <span>Spice level {meal.spice_level}</span>
        </div>

        <div style={{ display: "flex", justifyContent: "flex-end" }}>
          <Button
            variant={isOwnMeal ? "ghost" : "primary"}
            disabled={isOwnMeal}
            onClick={() => !isOwnMeal && onRequestSwap?.(meal)}
          >
            {isOwnMeal ? "Your meal" : "Request Swap"}
          </Button>
        </div>
      </div>
    </Card>
  );
}
