import localOptions from "@/lib/localOptions";
import { extend, get } from "lodash";
import { useCallback, useState } from "react";

function isAiQueryAvailable(dataSource) {
  return get(dataSource, "supports_ai_query", false);
}

export default function useAiQueryFlags(dataSource, query, setQuery) {
  const isAvailable = isAiQueryAvailable(dataSource);
  const [isChecked, setIsChecked] = useState(query.options.apply_ai_query ?? localOptions.get("applyAiQuery", false));
  query.options.apply_ai_query = isChecked;

  const setAiQuery = useCallback(
    (state) => {
      setIsChecked(state);
      localOptions.set("applyAiQuery", state);
      setQuery(extend(query.clone(), { options: { ...query.options, apply_ai_query: state } }));
    },
    [query, setQuery]
  );

  return [isAvailable, isChecked, setAiQuery];
}
