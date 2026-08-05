import useImmutableCallback from "@/lib/hooks/useImmutableCallback";
import AiService from "@/services/ai";
import recordEvent from "@/services/recordEvent";
import { get } from "lodash";
import { useEffect, useState } from "react";

export default function useAITypesList(settings, currentValues) {
  const [aiTypes, setAiTypes] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const ai_enabled = get(currentValues, "ai_enabled", false);

  const handleError = useImmutableCallback((error) => {
    console.error(error);
  });

  useEffect(() => {
    recordEvent("view", "list", "ai_types_list");

    if (!ai_enabled) {
      setAiTypes({});
      return;
    }

    let isCancelled = false;

    setIsLoading(true);

    AiService.types()
      .then((response) => {
        if (!isCancelled) {
          setAiTypes(get(response, "types", {}));
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
  }, [ai_enabled, handleError]);

  return { aiTypes, isLoading };
}
