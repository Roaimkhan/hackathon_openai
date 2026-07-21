import type { ButtonHTMLAttributes, PropsWithChildren } from "react";
import { classNames } from "../../lib/utils";

type ButtonProps = PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>> & {
  variant?: "primary" | "secondary" | "ghost";
  loading?: boolean;
};

export function Button({ children, className, variant = "primary", loading = false, disabled, ...props }: ButtonProps) {
  return (
    <button
      {...props}
      className={classNames("button", `button--${variant}`, className)}
      disabled={disabled || loading}
    >
      {loading ? "Please wait…" : children}
    </button>
  );
}
