import { useQuery } from "@tanstack/react-query";
import { getMyActivityFiltered } from "../api/threadApi";
import { PAGE_SIZES } from "../utils/constants";

/**
 * Hook for current user's activity timeline.
 */
export function useMyActivityList(range, type, page) {
  return useQuery({
    queryKey: ["my-activity", range, type, page],
    queryFn: () =>
      getMyActivityFiltered({
        range,
        type,
        page,
        size: PAGE_SIZES.ACTIVITY,
      }),
    keepPreviousData: true,
  });
}
