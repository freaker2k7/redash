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
  const [gettingAIAlerts, setGettingAIAlerts] = useState(false);
  const [aiAlerts, setAIAlerts] = useState([]);
  const [createdAIAlerts, setCreatedAIAlerts] = useState([]);

  const getAIAlerts = useCallback(() => {
    setGettingAIAlerts(true);
    setAIAlerts([]);

    axios
      .get(`api/ai/alerts/${query.id}`)
      .then((data) => {
        setGettingAIAlerts(false);
        setAIAlerts(data.alerts);
      })
      .catch(() => {
        setGettingAIAlerts(false);
        notification.error("Failed to update AI alerts");
      });
  }, [query.id]);

  useMemo(() => {
    getAIAlerts();
  }, [getAIAlerts]);

  const createNewAlert = useCallback(
    (alert) => {
      setCreatingAIAlert(alert.key);

      axios
        .post(`api/alerts`, {
          query_id: query.id,
          name: alert.name,
          options: alert.options,
          rearm: null,
        })
        .then((data) => {
          setCreatingAIAlert("");
          notification.success("AI alert created successfully");
          setCreatedAIAlerts((prev) => [...prev, alert.key]);
        })
        .catch(() => {
          setCreatingAIAlert("");
          notification.error("Failed to create AI alert");
        });
    },
    [query.id, dialog]
  );

  return (
    <Modal
      {...dialog.props}
      width={600}
      footer={
        <div className="d-flex justify-space-between">
          <Button className="ant-btn ant-btn-primary" onClick={getAIAlerts} disabled={gettingAIAlerts}>
            Resuggest
          </Button>
          <Button onClick={() => dialog.close(query)}>Close</Button>
        </div>
      }
    >
      <div className="query-ai-alerts-dialog-wrapper">
        <h5>AI Suggested Alerts</h5>
        <div className="m-b-10">
          {aiAlerts.length > 0 ? (
            <ul className="ai-alerts-list">
              {aiAlerts.map((alert, index) => (
                <Button
                  key={index}
                  loading={gettingAIAlerts || creatingAIAlert === alert.key}
                  onClick={() => createNewAlert(alert)}
                  disabled={createdAIAlerts.includes(alert.key)}
                >
                  {(creatingAIAlert === alert.key && <i className="zmdi zmdi-check" aria-hidden="true" />) ||
                    (createdAIAlerts.includes(alert.key) && (
                      <i className="zmdi zmdi-check-all" aria-hidden="true" />
                    ))}{" "}
                  {alert.name}
                  <small>[ {alert.key} ]</small>
                </Button>
              ))}
            </ul>
          ) : gettingAIAlerts ? (
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
