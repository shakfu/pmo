import { useQuery } from "@tanstack/react-query";

import { listBusinessUnits } from "../api/pmo";

export const BUSINESS_UNITS_QUERY_KEY = ["business-units"] as const;

export function useBusinessUnits() {
  return useQuery({
    queryKey: BUSINESS_UNITS_QUERY_KEY,
    queryFn: listBusinessUnits,
    staleTime: 1000 * 60 * 2,
  });
}
