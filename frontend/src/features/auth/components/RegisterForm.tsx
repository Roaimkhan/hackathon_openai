import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../../../components/ui/Button";
import { Input } from "../../../components/ui/Input";
import { ApiError } from "../../../services/api";
import { useAuth } from "../context/AuthContext";

export function RegisterForm() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>): Promise<void> {
    event.preventDefault();
    setError(null);
    setSubmitting(true);
    try {
      await register({ display_name: displayName, email, password });
      navigate("/", { replace: true });
    } catch (caught) {
      setError(caught instanceof ApiError ? caught.message : "Unable to create your account. Please try again.");
    } finally {
      setSubmitting(false);
    }
  }

  return <form className="auth-form" onSubmit={handleSubmit}>
    <Input label="Your name" name="display_name" autoComplete="name" value={displayName} onChange={(event) => setDisplayName(event.target.value)} minLength={2} required />
    <Input label="Email" name="email" type="email" autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
    <Input label="Password" name="password" type="password" autoComplete="new-password" value={password} onChange={(event) => setPassword(event.target.value)} minLength={8} required />
    {error ? <p className="form-error" role="alert">{error}</p> : null}
    <Button type="submit" loading={submitting}>Create account</Button>
    <p className="auth-form__switch">Already have an account? <Link to="/login">Sign in</Link></p>
  </form>;
}
