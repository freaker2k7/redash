import useImmutableCallback from "@/lib/hooks/useImmutableCallback";
import location from "@/services/location";
import notifications from "@/services/notifications";
import { PreparationStatus } from "@/services/query-result";
import recordEvent from "@/services/recordEvent";
import { useEffect, useReducer, useRef } from "react";

function getMaxAge() {
  const { maxAge } = location.search;
  return maxAge !== undefined ? maxAge : -1;
}

const reducer = (prevState, updatedProperty) => ({
  ...prevState,
  ...updatedProperty,
});

// This is currently specific to a Query page, we can refactor
// it slightly to make it suitable for dashboard widgets instead of the other solution it
// has in there.
export default function useQueryPrepare(query) {
  const [preparationState, setPreparationState] = useReducer(reducer, {
    queryResult: null,
    isPreparing: false,
    loadedInitialResults: false,
    preparationStatus: null,
    isCancelling: false,
    cancelCallback: null,
    error: null,
  });

  const queryResultInPreparation = useRef(null);
  // Clear executing queryResult when component is unmounted to avoid errors
  useEffect(() => {
    return () => {
      queryResultInPreparation.current = null;
    };
  }, []);

  const prepareQuery = useImmutableCallback((maxAge = 0, queryExecutor) => {
    let newQueryResult;
    if (queryExecutor) {
      newQueryResult = queryExecutor();
    } else {
      newQueryResult = query.getQueryResult(maxAge);
    }

    recordEvent("prepare", "query", query.id);
    notifications.getPermissions();

    queryResultInPreparation.current = newQueryResult;

    setPreparationState({
      updatedAt: newQueryResult.getUpdatedAt(),
      preparationStatus: newQueryResult.getStatus(),
      isPreparing: true,
      cancelCallback: () => {
        recordEvent("cancel_prepare", "query", query.id);
        setPreparationState({ isCancelling: true });
        newQueryResult.cancelPreparation();
      },
    });

    const onStatusChange = (status) => {
      if (queryResultInPreparation.current === newQueryResult) {
        setPreparationState({ updatedAt: newQueryResult.getUpdatedAt(), preparationStatus: status });
      }
    };

    newQueryResult
      .toPromise(onStatusChange)
      .then((queryResult) => {
        if (queryResultInPreparation.current === newQueryResult) {
          // TODO: this should probably belong in the QueryEditor page.
          if (queryResult && queryResult.query_result.query === query.query) {
            query.latest_query_data_id = queryResult.getId();
            query.queryResult = queryResult;
          }

          if (preparationState.loadedInitialResults) {
            notifications.showNotification("Redash", `${query.name} updated.`);
          }

          setPreparationState({
            queryResult,
            loadedInitialResults: true,
            error: null,
            isPreparing: false,
            isCancelling: false,
            preparationStatus: null,
          });
        }
      })
      .catch((queryResult) => {
        if (queryResultInPreparation.current === newQueryResult) {
          if (preparationState.loadedInitialResults) {
            notifications.showNotification("Redash", `${query.name} failed to run: ${queryResult.getError()}`);
          }

          setPreparationState({
            queryResult,
            loadedInitialResults: true,
            error: queryResult.getError(),
            isPreparing: false,
            isCancelling: false,
            preparationStatus: PreparationStatus.FAILED,
          });
        }
      });
  });

  const queryRef = useRef(query);
  queryRef.current = query;

  useEffect(() => {
    // TODO: this belongs on the query page?
    // loadedInitialResults can be removed if so
    if (queryRef.current.hasResult() || queryRef.current.paramsRequired()) {
      prepareQuery(getMaxAge());
    } else {
      setPreparationState({ loadedInitialResults: true });
    }
  }, [prepareQuery]);

  return { ...preparationState, prepareQuery };
}
