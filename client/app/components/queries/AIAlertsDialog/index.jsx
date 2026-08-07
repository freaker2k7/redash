import { DialogPropType, wrap as wrapDialog } from "@/components/DialogWrapper";
import LoadingState from "@/components/items-list/components/LoadingState";
import { axios } from "@/services/axios";
import notification from "@/services/notification";
import Button from "antd/lib/button";
import Modal from "antd/lib/modal";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";

import "./index.less";

function AIAlertsDialog({ dialog, ...props }) {
  const [query] = useState(props.query);
  const [creatingAIAlert, setCreatingAIAlert] = useState("");
  const [creatingAIAlerts, setCreatingAIAlerts] = useState(false);
  const [aiAlerts, setAIAlerts] = useState([]);

  useMemo(() => {
    setCreatingAIAlerts(true);
    axios
      .get(`api/ai/alerts/${query.id}`)
      .then((data) => {
        setCreatingAIAlerts(false);
        setAIAlerts(data.alerts);
      })
      .catch(() => {
        setCreatingAIAlerts(false);
        notification.error("Failed to update AI alerts");
      });
  }, [query.id]);

  const createNewAlert = useCallback(
    (alert) => {
      setCreatingAIAlert(alert.name);
      axios
        .post(`api/alerts`, {
          query_id: query.id,
          name: alert.name,
          options: alert.options,
        })
        .then((data) => {
          setCreatingAIAlert("");
          notification.success("AI alert created successfully");
          dialog.close(data);
        })
        .catch(() => {
          setCreatingAIAlert("");
          notification.error("Failed to create AI alert");
        });
    },
    [query.id, dialog]
  );

  return (
    <Modal {...dialog.props} width={600} footer={<Button onClick={() => dialog.close(query)}>Close</Button>}>
      <div className="query-ai-alerts-dialog-wrapper">
        <h5>AI Suggested Alerts</h5>
        <div className="m-b-10">
          {aiAlerts.length > 0 ? (
            <ul className="ai-alerts-list">
              {aiAlerts.map((alert, index) => (
                <Button
                  key={index}
                  loading={creatingAIAlerts || creatingAIAlert === alert.name}
                  onClick={() => createNewAlert(alert)}
                >
                  {alert.name}
                </Button>
              ))}
            </ul>
          ) : creatingAIAlerts ? (
            <LoadingState className="m-t-20" />
          ) : (
            <p>No AI suggested alerts.</p>
          )}
        </div>
      </div>
    </Modal>
  );
}

AIAlertsDialog.propTypes = {
  dialog: DialogPropType.isRequired,
  query: PropTypes.shape({
    id: PropTypes.number.isRequired,
  }).isRequired,
};

export default wrapDialog(AIAlertsDialog);
