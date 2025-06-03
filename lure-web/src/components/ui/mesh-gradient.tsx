"use client";

import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";
import { Gradient } from "@/ext/gradient";

export function MeshGradient() {
  const pathname = usePathname();
  const [isLoaded, setIsLoaded] = useState(false);

  useEffect(() => {
    const gradient = new Gradient();
    // @ts-ignore
    gradient.initGradient("#gradient-canvas");

    const timer = setTimeout(() => {
      setIsLoaded(true);
    }, 100);

    return () => clearTimeout(timer);
  }, []);

  const baseOpacity = pathname === "/" ? "1" : "0.65";
  const opacity = isLoaded ? baseOpacity : "0";
  const blur = pathname === "/" ? "none" : "blur(8px)";

  return (
    <canvas
      id="gradient-canvas"
      className="absolute inset-0 w-full h-full transition-all duration-500"
      style={
        {
          "--gradient-color-1": "#3d5652",
          "--gradient-color-2": "#5b7671",
          "--gradient-color-3": "#486661",
          "--gradient-color-4": "#2d4340",
          opacity,
          filter: blur,
        } as React.CSSProperties
      }
      data-transition-in
    />
  );
}
