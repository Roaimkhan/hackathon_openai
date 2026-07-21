import { useMemo, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/context/AuthContext";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { Card } from "../../components/ui/Card";
import { formatDate } from "../../lib/utils";
import type { ApiEnvelope, SwapResponse } from "../../services/types";

const statusColor: Record<string, string> = {
  pending: "#fef9c3",
  accepted: "#d8f1dc",
  rejected: "#fee2e2",
  completed: "#d8f1dc",
};

interface SwapCardProps {
  swap: SwapResponse;
  role: "incoming" | "outgoing";
  onAction: (swapId: string, action: "accept" | "reject" | "cancel") => void;
}

function SwapCard({ swap, role, onAction }: SwapCardProps) {
  const isIncoming = role === "incoming";
  return (
    <Card style={{ display: "grid", gap: "1rem", padding: "1.25rem", border: "1px solid #f1ddd0" }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
        <div>
          <p className="eyebrow" style={{ margin: 0 }}>{isIncoming ? "Incoming" : "Outgoing"}</p>
          <h3 style={{ margin: 0, fontSize: "1.2rem" }}>{swap.meal.title}</h3>
          <p style={{ margin: "0.5rem 0 0", color: "#64726c" }}>Requested on {formatDate(swap.created_at)}</p>
        </div>
        <Badge style={{ background: statusColor[swap.status] ?? "#e8f4e9", color: "#405048" }}>{swap.status.toUpperCase()}</Badge>
      </div>

      <div style={{ display: "grid", gap: "0.8rem", padding: "1rem", background: "#fbf7f2", borderRadius: "1rem" }}>
        <p style={{ margin: 0, fontWeight: 700 }}>Swap Details</p>
        <div style={{ display: "grid", gap: "0.5rem" }}>
          <span><strong>Requested meal:</strong> {swap.meal.title}</span>
          {swap.message ? <span><strong>Note:</strong> {swap.message}</span> : null}
        </div>
      </div>

      <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem", flexWrap: "wrap" }}>
        {isIncoming && swap.status === "pending" ? (
          <> 
            <Button variant="primary" onClick={() => onAction(swap.id, "accept")}>Accept</Button>
            <Button variant="ghost" onClick={() => onAction(swap.id, "reject")}>Reject</Button>
          </>
        ) : swap.status === "pending" ? (
          <Button variant="ghost" onClick={() => onAction(swap.id, "cancel")}>Cancel Request</Button>
        ) : null}
      </div>
    </Card>
  );
}

export function SwapInboxPage() {
  const [activeTab, setActiveTab] = useState<"incoming" | "outgoing">("incoming");
  const queryClient = useQueryClient();

  const { data, isLoading, isError } = useQuery<ApiEnvelope<SwapResponse[]>, ApiError>({
    queryKey: ["swaps", activeTab],
    queryFn: async () => api.getWithMeta<SwapResponse[]>(`/swaps?role=${activeTab === "incoming" ? "received" : "sent"}`),
    // The requester is a different user, so their inbox needs to observe updates
    // made by the recipient in another session.
    refetchInterval: 5_000,
    refetchOnWindowFocus: true,
  });

  const actionMutation = useMutation<unknown, ApiError, { swapId: string; action: "accept" | "reject" | "cancel" }>({
    mutationFn: async ({ swapId, action }) => {
      const body = { note: action === "cancel" ? "Cancelled by requester" : undefined };
      const endpoint = action === "cancel" ? "cancel" : action;
      return api.post(`/swaps/${swapId}/${endpoint}`, body);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["swaps"] }),
  });

  const navigate = useNavigate();
  const swaps = useMemo<SwapResponse[]>(() => data?.data ?? [], [data]);
  const incoming = activeTab === "incoming" ? swaps : [];
  const outgoing = activeTab === "outgoing" ? swaps : [];

  return (
    <main className="page-center" style={{ padding: "2rem" }}>
      <section style={{ width: "100%", maxWidth: "74rem" }}>
        <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem", alignItems: "center" }}>
          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
            <Button variant="ghost" onClick={() => navigate(-1)}>Back</Button>
            <Button variant="secondary" onClick={() => navigate("/feed")}>Browse feed</Button>
          </div>
          <div>
            <p className="eyebrow">Swap Inbox</p>
            <h1 style={{ margin: 0, fontSize: "2.5rem" }}>Manage your swap requests</h1>
            <p style={{ margin: "0.75rem 0 0", color: "#64726c", maxWidth: "48rem" }}>
              Review incoming offers, accept or reject requests, and track pending swaps you have sent.
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          <Button variant={activeTab === "incoming" ? "primary" : "secondary"} onClick={() => setActiveTab("incoming")}>Incoming</Button>
          <Button variant={activeTab === "outgoing" ? "primary" : "secondary"} onClick={() => setActiveTab("outgoing")}>Outgoing</Button>
        </div>

        {isLoading ? (
          <Card style={{ padding: "1.5rem" }}><p>Loading your swap requests…</p></Card>
        ) : isError ? (
          <Card style={{ padding: "1.5rem", background: "#fff1f0", borderColor: "#f9d1d0" }}><p>Unable to load swaps. Try again later.</p></Card>
        ) : null}

        {activeTab === "incoming" ? (
          incoming.length ? (
            <div style={{ display: "grid", gap: "1rem" }}>
              {incoming.map((swap) => <SwapCard key={swap.id} swap={swap} role="incoming" onAction={(swapId, action) => actionMutation.mutate({ swapId, action })} />)}
            </div>
          ) : (
            <Card style={{ padding: "1.5rem", textAlign: "center" }}><p>No incoming swap requests yet.</p></Card>
          )
        ) : outgoing.length ? (
          <div style={{ display: "grid", gap: "1rem" }}>
            {outgoing.map((swap) => <SwapCard key={swap.id} swap={swap} role="outgoing" onAction={(swapId, action) => actionMutation.mutate({ swapId, action })} />)}
          </div>
        ) : (
          <Card style={{ padding: "1.5rem", textAlign: "center" }}><p>No outgoing swap requests yet.</p></Card>
        )}
      </section>
    </main>
  );
}
