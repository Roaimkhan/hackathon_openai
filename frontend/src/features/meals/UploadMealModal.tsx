import { useMemo, useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { api, ApiError } from "../../services/api";
import { Button } from "../../components/ui/Button";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import type { MealCreateRequest, MealResponse } from "../../types/api";

interface UploadMealModalProps {
  open: boolean;
  onClose: () => void;
  onUploaded: (meal: MealResponse) => void;
}

export function UploadMealModal({ open, onClose, onUploaded }: UploadMealModalProps) {
  const [step, setStep] = useState(1);
  const [file, setFile] = useState<File | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [location, setLocation] = useState("");
  const [serverError, setServerError] = useState<string | null>(null);
  const [draftMeal, setDraftMeal] = useState<MealResponse | null>(null);
  const [analyzed, setAnalyzed] = useState(false);

  const createMealMutation = useMutation<MealResponse, ApiError, MealCreateRequest>({
    mutationFn: async (payload) => api.post<MealResponse>("/meals", payload),
  });

  const uploadImageMutation = useMutation<MealResponse, ApiError, string>({
    mutationFn: async (mealId) => {
      const formData = new FormData();
      if (!file) throw new Error("No file selected");
      formData.append("image", file, file.name);
      return api.upload<MealResponse>(`/meals/${mealId}/image-upload`, formData);
    },
  });

  const reset = () => {
    setStep(1);
    setFile(null);
    setTitle("");
    setDescription("");
    setLocation("");
    setServerError(null);
    setDraftMeal(null);
    setAnalyzed(false);
  };

  const handleClose = () => {
    reset();
    onClose();
  };

  const handleFileSelection = (selected: File | null) => {
    setFile(selected);
    if (selected) setStep(2);
  };

  const handleCreateDraft = async () => {
    setServerError(null);
    try {
      const payload: MealCreateRequest = {
        title,
        description,
      };
      if (location.trim()) payload.location = location.trim();
      const newMeal = await createMealMutation.mutateAsync(payload);
      setDraftMeal(newMeal);
      setStep(3);
      await new Promise((resolve) => setTimeout(resolve, 1200));
      setAnalyzed(true);
      setStep(4);
    } catch (caught) {
      setServerError(caught instanceof ApiError ? caught.message : "Unable to create meal draft.");
    }
  };

  const handleUploadImage = async () => {
    if (!draftMeal) return;
    setServerError(null);
    try {
      const updated = await uploadImageMutation.mutateAsync(draftMeal.id);
      onUploaded(updated);
      handleClose();
    } catch (caught) {
      setServerError(caught instanceof ApiError ? caught.message : "Unable to upload meal image.");
    }
  };

  const actionLabel = useMemo(() => {
    if (step === 1) return "Pick an image";
    if (step === 2) return "Create draft";
    if (step === 3) return "Analyzing...";
    return "Upload image";
  }, [step]);

  return (
    <Modal
      title="Upload a meal"
      open={open}
      onClose={handleClose}
      footer={
        <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
          <Button variant="ghost" onClick={handleClose}>Cancel</Button>
          {step === 2 ? (
            <Button onClick={handleCreateDraft} disabled={!title || createMealMutation.isPending}>{createMealMutation.isPending ? "Creating…" : "Create draft"}</Button>
          ) : step === 4 ? (
            <Button onClick={handleUploadImage} disabled={uploadImageMutation.isPending}>{uploadImageMutation.isPending ? "Uploading…" : "Confirm upload"}</Button>
          ) : null}
        </div>
      }
    >
      <div style={{ display: "grid", gap: "1.1rem" }}>
        {step === 1 ? (
          <div>
            <p>Start by selecting a meal photo. We’ll analyze the image and help you complete the meal profile.</p>
            <label htmlFor="meal-image" style={{ display: "grid", gap: "1rem", padding: "1.5rem", border: "2px dashed #d9ded9", borderRadius: "1rem", textAlign: "center", cursor: "pointer" }}>
              <span style={{ fontSize: "1rem", fontWeight: 700 }}>Drop image here or click to choose a file</span>
              <span style={{ color: "#64726c" }}>{file ? file.name : "PNG, JPG, or WEBP"}</span>
              <input id="meal-image" type="file" accept="image/*" onChange={(event) => handleFileSelection(event.target.files?.[0] ?? null)} style={{ display: "none" }} />
            </label>
          </div>
        ) : null}

        {step === 2 ? (
          <div style={{ display: "grid", gap: "1rem" }}>
            <Input label="Meal title" name="mealTitle" value={title} onChange={(event) => setTitle(event.target.value)} required />
            <label className="field" htmlFor="mealDescription">
              <span>Description (optional)</span>
              <textarea id="mealDescription" className="input" rows={4} value={description} onChange={(event) => setDescription(event.target.value)} />
            </label>
            <Input
              label="Meeting location (optional)"
              name="mealLocation"
              value={location}
              onChange={(event) => setLocation(event.target.value)}
              placeholder="e.g. F-7 Markaz, Islamabad"
            />
            {serverError ? <div className="form-error">{serverError}</div> : null}
          </div>
        ) : null}

        {step === 3 ? (
          <div style={{ padding: "2rem", textAlign: "center", background: "#f7f3ef", borderRadius: "1rem" }}>
            <p style={{ margin: 0, fontWeight: 700 }}>Analyzing macro profile with Vision AI…</p>
            <p style={{ margin: "0.75rem 0 0", color: "#64726c" }}>This may take a few seconds while we detect cuisine, spice, and dietary tags.</p>
          </div>
        ) : null}

        {step === 4 ? (
          <div style={{ display: "grid", gap: "1rem" }}>
            <p style={{ margin: 0, fontWeight: 700 }}>Review extracted meal details</p>
            <div style={{ background: "#faf7f3", borderRadius: "1rem", padding: "1rem" }}>
              <p style={{ margin: 0 }}><strong>Title:</strong> {draftMeal?.title ?? title}</p>
              <p style={{ margin: "0.5rem 0 0" }}><strong>Description:</strong> {(draftMeal?.description ?? description) || "No description provided"}</p>
              <p style={{ margin: "0.5rem 0 0" }}><strong>Analysis status:</strong> {draftMeal?.analysis_status ?? "pending"}</p>
              <p style={{ margin: "0.5rem 0 0" }}><strong>Added image:</strong> {file?.name}</p>
              {draftMeal?.location ?? location ? (
                <p style={{ margin: "0.5rem 0 0" }}><strong>Meeting location:</strong> {draftMeal?.location ?? location}</p>
              ) : null}
            </div>
            {serverError ? <div className="form-error">{serverError}</div> : null}
          </div>
        ) : null}
      </div>
    </Modal>
  );
}
