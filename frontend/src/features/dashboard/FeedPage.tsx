import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { MealCard } from "../../components/MealCard";
import { SwapRequestModal } from "../swaps/SwapRequestModal";
import { UploadMealModal } from "../meals";
import type { FeedResponse, MealCardItem } from "../../types/api";

function SkeletonCard() {
  return (
    <Card style={{ padding: "1.25rem", marginBottom: "1rem", background: "#f8f5f2" }}>
      <div style={{ display: "grid", gap: "0.85rem" }}>
        <div style={{ height: "1.25rem", width: "45%", background: "#e7e2dd", borderRadius: "999px" }} />
        <div style={{ height: "1rem", width: "60%", background: "#ece8e2", borderRadius: "999px" }} />
        <div style={{ height: "3rem", width: "100%", background: "#ece8e2", borderRadius: "1rem" }} />
      </div>
    </Card>
  );
}

export function FeedPage() {
  const [selectedTargetMeal, setSelectedTargetMeal] = useState<MealCardItem | null>(null);
  const [isUploadOpen, setUploadOpen] = useState(false);
  const queryClient = useQueryClient();

  const { data, isLoading, isError, error } = useQuery<
    FeedResponse,
    ApiError,
    FeedResponse,
    readonly ["feed"]
  >({
    queryKey: ["feed"],
    queryFn: async () => api.get<FeedResponse>(`/feed`),
  });

  const summary = useMemo(() => {
    if (!data) return "Browse the meals ranked by compatibility with your profile and proximity.";
    return `${data.count} meals available nearby`;
  }, [data]);

  return (
    <main className="page-center" style={{ padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: "72rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <div>
            <p className="eyebrow">Feed</p>
            <h1 style={{ margin: 0, fontSize: "2.5rem" }}>Meals near you, ranked by AI compatibility.</h1>
            <p style={{ margin: "0.75rem 0 0", color: "#64726c", maxWidth: "48rem" }}>{summary}</p>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <Button variant="secondary" onClick={() => setUploadOpen(true)}>Add meal</Button>
            <Link to="/meals"><Button variant="secondary">My meals</Button></Link>
            <Button variant="secondary" onClick={() => window.location.reload()}>Refresh</Button>
            <Link to="/swaps"><Button variant="ghost">Swap inbox</Button></Link>
          </div>
        </div>

        {isLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : null}

        {data?.items.length ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 18rem), 22rem))", gap: "1rem" }}>
            {data.items.map((meal) => (
              <MealCard key={meal.id} meal={meal} onRequestSwap={(item) => setSelectedTargetMeal(item)} />
            ))}
          </div>
        ) : null}

        {isError ? (
          <Card style={{ padding: "1.5rem", textAlign: "center", background: "#fff1f0", borderColor: "#f9d1d0" }}>
            <p style={{ margin: 0 }}>{error instanceof ApiError ? error.message : "Unable to load nearby meals."}</p>
          </Card>
        ) : null}

        {data && data.items.length === 0 ? (
          <Card style={{ padding: "1.5rem", textAlign: "center" }}>
            <p style={{ margin: 0 }}>No meals found in the selected radius. Try increasing the radius or adding a new meal.</p>
          </Card>
        ) : null}

        <SwapRequestModal
          open={selectedTargetMeal !== null}
          targetMeal={selectedTargetMeal}
          onClose={() => setSelectedTargetMeal(null)}
        />
        <UploadMealModal
          open={isUploadOpen}
          onClose={() => setUploadOpen(false)}
          onUploaded={() => {
            setUploadOpen(false);
            queryClient.invalidateQueries({ queryKey: ["feed"] });
          }}
        />
      </section>
    </main>
  );
}
