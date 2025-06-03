"use client";

import { MeshGradient } from "./mesh-gradient";

export function GradientContainer() {
  return (
    <div className="fixed inset-0 transition-[filter] duration-500">
      <MeshGradient />
    </div>
  );
}
