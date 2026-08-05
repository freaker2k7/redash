import useImmutableCallback from "@/lib/hooks/useImmutableCallback";
import AiService from "@/services/ai";
import recordEvent from "@/services/recordEvent";
import { get } from "lodash";
import { useEffect, useState } from "react";

export default function useAIModelsList(settings, currentValues) {
  const [modelsList, setModelsList] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const ai_enabled = get(currentValues, "ai_enabled", false);
  const ai_model = get(currentValues, "ai_model", get(settings, "ai_model", "huggingface-local"));

  const handleError = useImmutableCallback((error) => {
    console.error(error);
  });

  useEffect(() => {
    recordEvent("view", "list", `${ai_model}_models_list`);

    if (!ai_enabled) {
      setModelsList({});
      return;
    }

    let isCancelled = false;

    setIsLoading(true);

    AiService.get({ model: ai_model })
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
  }, [ai_model, ai_enabled, handleError, settings, currentValues]);

  return { modelsList, isLoading };
}
