import type { HTMLAttributes, PropsWithChildren } from "react";
import { classNames } from "../../lib/utils";

export function Card({ children, className, ...props }: PropsWithChildren<HTMLAttributes<HTMLDivElement>>) {
  return <section {...props} className={classNames("card", className)}>{children}</section>;
}
