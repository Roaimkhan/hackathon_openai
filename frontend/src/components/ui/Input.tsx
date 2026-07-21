import { forwardRef } from "react";
import type { InputHTMLAttributes } from "react";
import { classNames } from "../../lib/utils";

type InputProps = InputHTMLAttributes<HTMLInputElement> & { label: string; error?: string };

export const Input = forwardRef<HTMLInputElement, InputProps>(function Input(
  { label, error, className, id, ...props },
  ref,
) {
  const inputId = id ?? props.name;
  return (
    <label className="field" htmlFor={inputId}>
      <span>{label}</span>
      <input ref={ref} id={inputId} className={classNames("input", error && "input--error", className)} {...props} />
      {error ? <small className="field__error">{error}</small> : null}
    </label>
  );
});
