import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { MealCard } from "../../components/MealCard";
import { SwapRequestModal } from "../swaps/SwapRequestModal";
import type { ApiEnvelope } from "../../services/types";
import type { SearchRequest, SearchResponse, SearchIntentResult, MealCardItem } from "../../types/api";
import { formatDistance } from "../../lib/utils";

const DEFAULT_LOCATION = { latitude: 33.7182, longitude: 73.0605 };

function scoreBadgeStyle(score: number) {
  if (score > 75) return { background: "#d8f1dc", color: "#166534" };
  if (score >= 50) return { background: "#fef9c3", color: "#92400e" };
  return { background: "#fee2e2", color: "#991b1b" };
}


function SkeletonCard() {
  return (
    <Card className="meal-card--skeleton" style={{ padding: "1.25rem", marginBottom: "1rem", background: "#f8f5f2" }}>
      <div style={{ display: "grid", gap: "0.75rem" }}>
        <div style={{ height: "1.25rem", width: "40%", background: "#e7e2dd", borderRadius: "999px" }} />
        <div style={{ height: "1rem", width: "55%", background: "#ece8e2", borderRadius: "999px" }} />
        <div style={{ height: "3rem", width: "100%", background: "#ece8e2", borderRadius: "1rem" }} />
      </div>
    </Card>
  );
}

export function SearchPage() {
  const [queryText, setQueryText] = useState("");
  const [latitude, setLatitude] = useState(DEFAULT_LOCATION.latitude.toString());
  const [longitude, setLongitude] = useState(DEFAULT_LOCATION.longitude.toString());
  const [radiusKm, setRadiusKm] = useState("10");
  const [searchRequest, setSearchRequest] = useState<SearchRequest | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedTargetMeal, setSelectedTargetMeal] = useState<MealCardItem | null>(null);

  const { data: result, isFetching, isError } = useQuery<
    ApiEnvelope<SearchResponse>,
    ApiError,
    ApiEnvelope<SearchResponse>,
    readonly ["search", SearchRequest | null]
  >({
    queryKey: ["search", searchRequest] as const,
    queryFn: async () => {
      if (!searchRequest) throw new Error("Search request missing");
      const query = new URLSearchParams({
        q: searchRequest.q,
        latitude: searchRequest.latitude?.toString() ?? "",
        longitude: searchRequest.longitude?.toString() ?? "",
        radius_km: searchRequest.radius_km?.toString() ?? "",
        limit: searchRequest.limit?.toString() ?? "12",
      });
      return api.getWithMeta<SearchResponse>(`/search?${query.toString()}`);
    },
    enabled: searchRequest !== null,
  });

  const intent = useMemo<SearchIntentResult | null>(() => {
    if (!result?.meta) return null;
    return (result.meta as Record<string, unknown>).applied_filters as SearchIntentResult | null;
  }, [result]);

  const handleSearch = (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setErrorMessage(null);
    setSearchRequest({
      q: queryText,
      latitude: Number(latitude),
      longitude: Number(longitude),
      radius_km: Number(radiusKm),
      limit: 12,
    });
  };

  return (
    <main className="page-center" style={{ padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: "72rem" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem" }}>
          <div>
            <p className="eyebrow">Search</p>
            <h1 style={{ margin: 0, fontSize: "2.5rem" }}>Find the perfect meal swap near you.</h1>
            <p style={{ margin: "0.75rem 0 0", color: "#64726c", maxWidth: "48rem" }}>
              Use natural language to search for dietary matches, cuisine, spice, and nearby meals.
            </p>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
            <Link to="/feed"><Button variant="secondary">Nearby feed</Button></Link>
            <Button variant="ghost" onClick={() => {
              setLatitude(DEFAULT_LOCATION.latitude.toString());
              setLongitude(DEFAULT_LOCATION.longitude.toString());
              setRadiusKm("10");
            }}>Use demo location</Button>
          </div>
        </div>

        <form onSubmit={handleSearch} style={{ display: "grid", gap: "1rem", marginBottom: "1.5rem" }}>
          <Input label="What are you craving?" name="query" value={queryText} onChange={(event) => setQueryText(event.target.value)} placeholder="High protein lunch under 500 cals near me" required />
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, minmax(0, 1fr))", gap: "1rem" }}>
            <Input label="Latitude" name="latitude" type="number" step="0.0001" value={latitude} onChange={(event) => setLatitude(event.target.value)} required />
            <Input label="Longitude" name="longitude" type="number" step="0.0001" value={longitude} onChange={(event) => setLongitude(event.target.value)} required />
            <Input label="Radius (km)" name="radius" type="number" step="1" min="1" value={radiusKm} onChange={(event) => setRadiusKm(event.target.value)} required />
          </div>
          <div style={{ display: "flex", justifyContent: "flex-end" }}>
            <Button type="submit">Search meals</Button>
          </div>
        </form>

        {errorMessage ? <div className="form-error" role="alert" style={{ marginBottom: "1rem" }}>{errorMessage}</div> : null}

        {intent ? (
          <Card className="intent-card" style={{ marginBottom: "1.5rem", padding: "1.25rem", background: "#f7f3ef" }}>
            <h2 style={{ margin: 0, fontSize: "1.2rem" }}>Detected search intent</h2>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginTop: "0.95rem" }}>
              <span><strong>Cuisine:</strong> {intent.cuisine ?? "Any"}</span>
              <span><strong>Max spice:</strong> {intent.max_spice_level ?? "Any"}</span>
              <span><strong>Tags:</strong> {intent.tags.length ? intent.tags.join(", ") : "None"}</span>
              <span><strong>Radius:</strong> {intent.radius_km ? `${intent.radius_km} km` : "Default"}</span>
            </div>
          </Card>
        ) : null}

        <section>
          {isFetching && !result ? (
            <>
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </>
          ) : null}

          {result?.data.items.length ? (
            <div style={{ display: "grid", gap: "1rem" }}>
              {result.data.items.map((meal) => (
                <MealCard key={meal.id} meal={meal} onRequestSwap={(item) => setSelectedTargetMeal(item)} />
              ))}
            </div>
          ) : null}

          {result && result.data.items.length === 0 ? (
            <Card style={{ padding: "1.5rem", textAlign: "center" }}>
              <p style={{ margin: 0 }}>No meals matched your search. Try a broader query or a larger radius.</p>
            </Card>
          ) : null}

          <SwapRequestModal
            open={selectedTargetMeal !== null}
            targetMeal={selectedTargetMeal}
            onClose={() => setSelectedTargetMeal(null)}
          />

          {isError && !isFetching && !result ? (
            <Card style={{ padding: "1.5rem", textAlign: "center", background: "#fff1f0", borderColor: "#f9d1d0" }}>
              <p style={{ margin: 0 }}>Unable to load search results. Please try again.</p>
            </Card>
          ) : null}
        </section>
      </section>
    </main>
  );
}
