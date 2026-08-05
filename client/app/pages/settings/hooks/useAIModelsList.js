import useImmutableCallback from "@/lib/hooks/useImmutableCallback";
import AiService from "@/services/ai";
import recordEvent from "@/services/recordEvent";
import { get } from "lodash";
import { useEffect, useMemo, useState } from "react";

export default function useAIModelsList(currentValues) {
  const [modelsList, setModelsList] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [aiCacheKey, setAiCacheKey] = useState("");

  const handleError = useImmutableCallback((error) => {
    console.error(error);
  });

  useEffect(() => {
    console.log("useAIModelsList currentValues", currentValues, "aiCacheKey", aiCacheKey);

    const ai_enabled = get(currentValues, "ai_enabled", false);

    if (!ai_enabled) {
      setModelsList({});
      return;
    }

    const ai_type = get(currentValues, "ai_type");
    const ai_token = get(currentValues, "ai_token");
    const ai_host = get(currentValues, "ai_host");
    const key = `${ai_type}_${ai_token}_${ai_host}`;

    if (aiCacheKey === key) {
      return;
    }

    setAiCacheKey(key);

    let isCancelled = false;

    recordEvent("view", "list", `${ai_type.replace(/_/g, "-")}_models_list`);

    setIsLoading(true);

    AiService.models({ type: ai_type, host: ai_host, token: ai_token })
      .then((response) => {
        if (!isCancelled) {
          setModelsList(get(response, "models", {}));
          setIsLoading(false);
        }
      })
      .catch((error) => {
        if (!isCancelled) {
          setIsLoading(false);
          handleError(error);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [handleError, currentValues]);

  const memoizedModelsList = useMemo(() => modelsList, [aiCacheKey, modelsList]);

  return { modelsList: memoizedModelsList, isLoading };
}
