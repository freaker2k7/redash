import useImmutableCallback from "@/lib/hooks/useImmutableCallback";
import AiService from "@/services/ai";
import recordEvent from "@/services/recordEvent";
import { get } from "lodash";
import { useEffect, useState } from "react";

export default function useAITypesList(currentValues) {
  const [aiTypes, setAiTypes] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const handleError = useImmutableCallback((error) => {
    console.error(error);
  });

  useEffect(() => {
    const ai_enabled = get(currentValues, "ai_enabled", false);

    if (!ai_enabled) {
      setAiTypes({});
      return;
    }

    recordEvent("view", "list", "ai_types_list");

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
  }, [handleError, currentValues]);

  return { aiTypes, isLoading };
}
