import { api } from "./api";
import type { AuthSession, LoginPayload, RegisterPayload, User } from "./types";

export const authService = {
  register(payload: RegisterPayload): Promise<AuthSession> {
    return api.post<AuthSession>("/auth/register", payload);
  },
  login(payload: LoginPayload): Promise<AuthSession> {
    return api.post<AuthSession>("/auth/login", payload);
  },
  currentUser(): Promise<User> {
    return api.get<User>("/auth/me");
  },
};
