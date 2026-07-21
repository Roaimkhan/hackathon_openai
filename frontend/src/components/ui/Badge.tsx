import type { HTMLAttributes, PropsWithChildren } from "react";
import { classNames } from "../../lib/utils";

export function Badge({ children, className, ...props }: PropsWithChildren<HTMLAttributes<HTMLSpanElement>>) {
  return <span {...props} className={classNames("badge", className)}>{children}</span>;
}
