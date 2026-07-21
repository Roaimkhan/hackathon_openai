import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { UploadMealModal } from "./UploadMealModal";
import { formatDate } from "../../lib/utils";
import type { MealResponse } from "../../types/api";

function MealRow({ meal, onRemove }: { meal: MealResponse; onRemove: (id: string) => void }) {
  const imageUrl = meal.images?.[0]?.public_url;
  return (
    <Card style={{ display: "grid", gap: "1rem", padding: "0", border: "1px solid #f1ddd0", overflow: "hidden", minHeight: "10rem" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr", gap: "1rem" }}>
        <div style={{ display: "grid", gridTemplateColumns: "12rem 1fr", minHeight: "10rem", overflow: "hidden" }}>
          <div style={{ background: "#f8f3ec", minHeight: "10rem", overflow: "hidden" }}>
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={meal.title}
                style={{ width: "100%", height: "100%", objectFit: "cover", objectPosition: "center" }}
              />
            ) : (
              <div style={{ width: "100%", height: "100%", display: "grid", placeItems: "center", color: "#64726c", padding: "1rem", textAlign: "center" }}>
                No meal image
              </div>
            )}
          </div>
          <div style={{ display: "grid", gap: "0.75rem", padding: "1rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "flex-start", flexWrap: "wrap" }}>
              <div>
                <h2 style={{ margin: 0, fontSize: "1.25rem" }}>{meal.title}</h2>
                <p style={{ margin: "0.5rem 0 0", color: "#64726c" }}>{meal.description}</p>
              </div>
              <Badge style={{ background: meal.analysis_status === "complete" ? "#d8f1dc" : "#fef9c3", color: meal.analysis_status === "complete" ? "#166534" : "#92400e", whiteSpace: "nowrap" }}>
                {meal.analysis_status}
              </Badge>
            </div>
            <div style={{ display: "grid", gap: "0.35rem", color: "#405048", fontSize: "0.95rem" }}>
              {meal.cuisine ? <span><strong>Cuisine:</strong> {meal.cuisine}</span> : null}
              <span><strong>Spice level:</strong> {meal.spice_level}</span>
              <span><strong>Tags:</strong> {meal.dietary_tags.length ? meal.dietary_tags.join(", ") : "None"}</span>
              <span><strong>Created:</strong> {formatDate(meal.created_at)}</span>
            </div>
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", padding: "0 1rem 1rem", gap: "0.75rem" }}>
          <Button variant="ghost" onClick={() => onRemove(meal.id)}>Remove listing</Button>
        </div>
      </div>
    </Card>
  );
}

export function MyMealsPage() {
  const [isUploadOpen, setUploadOpen] = useState(false);
  const queryClient = useQueryClient();

  const deleteMutation = useMutation<unknown, ApiError, string>({
    mutationFn: async (mealId) => api.delete(`/meals/${mealId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["meals", "mine"] });
      queryClient.invalidateQueries({ queryKey: ["feed"] });
    },
  });

  const { data, isLoading, isError, error } = useQuery<MealResponse[], ApiError>({
    queryKey: ["meals", "mine"],
    queryFn: async () => api.get<MealResponse[]>("/meals/mine"),
  });

  return (
    <main className="page-center" style={{ padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: "72rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem", alignItems: "center" }}>
          <div>
            <p className="eyebrow">My Meals</p>
            <h1 style={{ margin: 0, fontSize: "2.5rem" }}>Your active meal listings</h1>
            <p style={{ margin: "0.75rem 0 0", color: "#64726c", maxWidth: "48rem" }}>
              Add a meal here so other people can request swaps from your available menu.
            </p>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
            <Button variant="secondary" onClick={() => setUploadOpen(true)}>Add meal</Button>
          </div>
        </div>

        {isLoading ? (
          <Card style={{ padding: "1.5rem" }}><p>Loading your meals…</p></Card>
        ) : isError ? (
          <Card style={{ padding: "1.5rem", background: "#fff1f0", borderColor: "#f9d1d0" }}><p>{error instanceof ApiError ? error.message : "Unable to load your meals."}</p></Card>
        ) : null}

        {data && data.length ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(min(100%, 22rem), 34rem))", gap: "1rem" }}>
            {data.map((meal) => <MealRow key={meal.id} meal={meal} onRemove={(id) => {
              if (!window.confirm("Remove this meal listing?")) return;
              deleteMutation.mutate(id);
            }} />)}
          </div>
        ) : null}

        {data && data.length === 0 ? (
          <Card style={{ padding: "1.5rem", textAlign: "center" }}>
            <p style={{ margin: 0 }}>You have not added any meals yet. Add one to start receiving swap requests.</p>
          </Card>
        ) : null}

        <UploadMealModal
          open={isUploadOpen}
          onClose={() => setUploadOpen(false)}
          onUploaded={() => {
            setUploadOpen(false);
            queryClient.invalidateQueries({ queryKey: ["meals", "mine"] });
            queryClient.invalidateQueries({ queryKey: ["feed"] });
          }}
        />
      </section>
    </main>
  );
}
