import { Card } from "../../../components/ui/Card";
import { LoginForm } from "../components/LoginForm";

export function LoginPage() {
  return <main className="auth-page"><section className="auth-page__intro"><p className="eyebrow">TableSwap</p><h1>Share a meal. Meet your neighborhood.</h1><p>Discover homemade meals matched to your taste.</p></section><Card className="auth-card"><h2>Welcome back</h2><p>Sign in to see what’s cooking nearby.</p><LoginForm /></Card></main>;
}
