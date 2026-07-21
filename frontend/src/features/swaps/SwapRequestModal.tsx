import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Modal } from "../../components/ui/Modal";
import { Card } from "../../components/ui/Card";
import { Badge } from "../../components/ui/Badge";
import type { ApiEnvelope } from "../../services/types";
import type { MealResponse } from "../../types/api";

interface SwapRequestModalProps {
  open: boolean;
  onClose: () => void;
  targetMeal: { id: string; title: string; image_url?: string | null } | null;
}

export function SwapRequestModal({ open, onClose, targetMeal }: SwapRequestModalProps) {
  const [selectedMealId, setSelectedMealId] = useState<string | null>(null);
  const [note, setNote] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const queryClient = useQueryClient();

  const { data: myMeals, isLoading: isMealsLoading } = useQuery<ApiEnvelope<MealResponse[]>, ApiError>({
    queryKey: ["meals", "mine"],
    queryFn: async () => api.getWithMeta<MealResponse[]>("/meals/mine"),
    enabled: open,
  });

  const createSwapMutation = useMutation<unknown, ApiError, { meal_id: string; message?: string }>({
    mutationFn: async (payload) => api.post("/swaps", payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["swaps"] });
      window.alert("Swap request sent successfully.");
      setSelectedMealId(null);
      setNote("");
      onClose();
    },
  });

  const availableMeals = useMemo(() => myMeals?.data ?? [], [myMeals]);

  const handleSubmit = async () => {
    if (!targetMeal || !selectedMealId) {
      setErrorMessage("Select one of your meals to offer for this swap.");
      return;
    }
    setErrorMessage(null);
    try {
      await createSwapMutation.mutateAsync({
        meal_id: targetMeal.id,
        message: note.trim() || undefined,
      });
    } catch (error) {
      setErrorMessage(error instanceof ApiError ? error.message : "Unable to submit swap request.");
    }
  };

  return (
    <Modal
      title={targetMeal ? `Swap request for ${targetMeal.title}` : "Request swap"}
      open={open}
      onClose={onClose}
      footer={
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
          <Button variant="ghost" onClick={onClose}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            disabled={!selectedMealId || createSwapMutation.isPending}
          >
            {createSwapMutation.isPending ? "Sending request…" : "Send swap request"}
          </Button>
        </div>
      }
    >
      <div style={{ display: "grid", gap: "1rem" }}>
        <p style={{ margin: 0, color: "#45503f" }}>
          Choose one of your active meals to offer in exchange and add an optional note.
        </p>

        <div style={{ display: "grid", gap: "0.75rem" }}>
          {isMealsLoading ? (
            Array.from({ length: 3 }).map((_, index) => (
              <Card
                key={`placeholder-${index}`}
                style={{ border: "1px solid #f1ddd0", background: "#fff", opacity: 0.7, padding: "1rem" }}
              >
                <div style={{ minHeight: "4.5rem", display: "grid", placeItems: "center", color: "#a1a8a0" }}>Loading your meals…</div>
              </Card>
            ))
          ) : (
            availableMeals.map((meal) => (
              <Card
                key={meal.id}
                className={selectedMealId === meal.id ? "selected-swap-meal" : undefined}
                style={{
                  border: selectedMealId === meal.id ? "2px solid #d95035" : "1px solid #f1ddd0",
                  cursor: "pointer",
                  background: "#fff",
                }}
                onClick={() => setSelectedMealId(meal.id)}
              >
                <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", alignItems: "center" }}>
                  <strong>{meal.title}</strong>
                  <Badge className="badge" style={{ background: selectedMealId === meal.id ? "#d95035" : "#e8f4e9", color: selectedMealId === meal.id ? "white" : "#2f6d43" }}>
                    Offer
                  </Badge>
                </div>
                <p style={{ margin: "0.5rem 0 0", color: "#64726c" }}>{meal.cuisine} · {meal.dietary_tags.join(" · ") || "No tags"}</p>
              </Card>
            ))
          )}
          {availableMeals.length === 0 && !isMealsLoading ? (
            <Card style={{ background: "#fff7f2", border: "1px solid #fde2d3" }}>
              <p style={{ margin: 0, color: "#7b4b3a" }}>No active meals found. Add a meal first before sending a swap request.</p>
            </Card>
          ) : null}
        </div>

        <Input label="Add a note (optional)" name="swapNote" value={note} onChange={(event) => setNote(event.target.value)} />
        {errorMessage ? <div className="form-error" role="alert">{errorMessage}</div> : null}
      </div>
    </Modal>
  );
}
