import { Card } from "../../../components/ui/Card";
import { RegisterForm } from "../components/RegisterForm";

export function RegisterPage() {
  return <main className="auth-page"><section className="auth-page__intro"><p className="eyebrow">TableSwap</p><h1>Good food deserves good company.</h1><p>Start swapping homemade meals with people nearby.</p></section><Card className="auth-card"><h2>Create your account</h2><p>It takes less than a minute.</p><RegisterForm /></Card></main>;
}
