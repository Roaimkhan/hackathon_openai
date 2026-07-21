import type { User } from "../services/types";

const TOKEN_KEY = "tableswap.access_token";
const USER_KEY = "tableswap.user";

function canUseStorage(): boolean {
  return typeof window !== "undefined" && typeof window.localStorage !== "undefined";
}

function readJson<T>(key: string): T | null {
  if (!canUseStorage()) return null;
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    window.localStorage.removeItem(key);
    return null;
  }
}

export const authStorage = {
  getToken(): string | null {
    return canUseStorage() ? window.localStorage.getItem(TOKEN_KEY) : null;
  },
  setToken(token: string): void {
    if (canUseStorage()) window.localStorage.setItem(TOKEN_KEY, token);
  },
  getUser(): User | null {
    return readJson<User>(USER_KEY);
  },
  setUser(user: User): void {
    if (canUseStorage()) window.localStorage.setItem(USER_KEY, JSON.stringify(user));
  },
  clear(): void {
    if (!canUseStorage()) return;
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
  },
};
