import { Link, NavLink, Navigate, Outlet, Route, Routes, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/Button";
import { AuthGuard } from "../features/auth/components/AuthGuard";
import { useAuth } from "../features/auth/context/AuthContext";
import { LoginPage } from "../features/auth/pages/LoginPage";
import { RegisterPage } from "../features/auth/pages/RegisterPage";
import { FeedPage } from "../features/dashboard";
import { SearchPage } from "../features/search";
import { SwapInboxPage } from "../features/swaps";
import { MyMealsPage } from "../features/meals";

function HomePage() {
  const { user } = useAuth();
  const navigate = useNavigate();

  return (
    <main className="page-center">
      <section className="welcome">
        <p className="eyebrow">TableSwap</p>
        <h1>Welcome, {user?.display_name}</h1>
        <p>Your nearby meal feed is coming next.</p>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", justifyContent: "center" }}>
          <Button variant="primary" onClick={() => navigate("/feed")}>Browse feed</Button>
          <Button variant="secondary" onClick={() => navigate("/meals")}>My meals</Button>
          <Button variant="secondary" onClick={() => navigate("/swaps")}>Swap inbox</Button>
        </div>
      </section>
    </main>
  );
}

function AppShell() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1rem", flexWrap: "wrap", padding: "1rem 2rem", background: "#fff", borderBottom: "1px solid #ece6df" }}>
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", alignItems: "center" }}>
          <Link to="/feed" style={{ fontWeight: 700, textDecoration: "none", color: "#111" }}>TableSwap</Link>
          <NavLink to="/feed" style={({ isActive }) => ({ padding: "0.6rem 0.95rem", borderRadius: "999px", textDecoration: "none", color: isActive ? "#111" : "#64726c", background: isActive ? "#f4efe6" : "transparent" })}>
            Feed
          </NavLink>
          <NavLink to="/meals" style={({ isActive }) => ({ padding: "0.6rem 0.95rem", borderRadius: "999px", textDecoration: "none", color: isActive ? "#111" : "#64726c", background: isActive ? "#f4efe6" : "transparent" })}>
            My meals
          </NavLink>
          <NavLink to="/swaps" style={({ isActive }) => ({ padding: "0.6rem 0.95rem", borderRadius: "999px", textDecoration: "none", color: isActive ? "#111" : "#64726c", background: isActive ? "#f4efe6" : "transparent" })}>
            Swap inbox
          </NavLink>
          <NavLink to="/search" style={({ isActive }) => ({ padding: "0.6rem 0.95rem", borderRadius: "999px", textDecoration: "none", color: isActive ? "#111" : "#64726c", background: isActive ? "#f4efe6" : "transparent" })}>
            Search
          </NavLink>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", flexWrap: "wrap" }}>
          {user ? <span style={{ color: "#405048" }}>Signed in as {user.display_name}</span> : null}
          <Button variant="ghost" onClick={() => { logout(); navigate("/login"); }}>
            Sign out
          </Button>
        </div>
      </header>
      <Outlet />
    </>
  );
}

export function AppRoutes() {
  return (
    <Routes>
      <Route element={<AuthGuard><AppShell /></AuthGuard>}>
        <Route path="/" element={<HomePage />} />
        <Route path="/feed" element={<FeedPage />} />
        <Route path="/search" element={<SearchPage />} />
        <Route path="/meals" element={<MyMealsPage />} />
        <Route path="/swaps" element={<SwapInboxPage />} />
      </Route>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
