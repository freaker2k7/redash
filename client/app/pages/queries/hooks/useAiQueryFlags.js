import useOrganizationSettings from "@/pages/settings/hooks/useOrganizationSettings";
import { extend, get } from "lodash";
import { useCallback, useState } from "react";

function isAiQueryAvailable(dataSource) {
  return get(dataSource, "supports_ai_query", false);
}

export default function useAiQueryFlags(dataSource, query, setQuery) {
  const { settings } = useOrganizationSettings({ onError: () => {} });
  const isAvailable = settings.ai_enabled && isAiQueryAvailable(dataSource);
  const [isChecked, setIsChecked] = useState(isAvailable && query.options.apply_ai_query);
  query.options.apply_ai_query = isChecked;

  const setAiQuery = useCallback(
    (state) => {
      setIsChecked(state);
      setQuery(extend(query.clone(), { options: { ...query.options, apply_ai_query: state } }));
    },
    [query, setQuery]
  );

  return [isAvailable, isChecked, setAiQuery];
}
