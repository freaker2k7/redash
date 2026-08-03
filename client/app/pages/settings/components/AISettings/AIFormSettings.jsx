import DynamicComponent from "@/components/DynamicComponent";
import Form from "antd/lib/form";
import Input from "antd/lib/input";
import Radio from "antd/lib/radio";
import Select from "antd/lib/select";
import Skeleton from "antd/lib/skeleton";
import React from "react";
import { SettingsEditorDefaultProps, SettingsEditorPropTypes } from "../prop-types";

export default function AIFormSettings(props) {
  const { values, onChange, loading } = props;

  return (
    <DynamicComponent name="OrganizationSettings.AIFormSettings" {...props}>
      <Form.Item label="AI Enabled">
        {loading ? (
          <Skeleton title={{ width: 300 }} paragraph={false} active />
        ) : (
          <Radio.Group value={values.ai_enabled} onChange={(e) => onChange({ ai_enabled: e.target.value })}>
            <Radio value={false}>Disabled</Radio>
            <Radio value={true}>Enabled</Radio>
          </Radio.Group>
        )}
      </Form.Item>
      {values.ai_enabled && (
        <>
          <Form.Item label="AI Type">
            {loading ? (
              <Skeleton title={{ width: 300 }} paragraph={false} active />
            ) : (
              <Select value={values.ai_type || "huggingface-local"} onChange={(value) => onChange({ ai_type: value })}>
                <Select.Option value="huggingface-local">HuggingFace (Local)</Select.Option>
                <Select.Option value="huggingface-remote" disabled>
                  HuggingFace (Remote) [Coming Soon]
                </Select.Option>
                <Select.Option value="ollama-remote" disabled>
                  Ollama (Remote) [Coming Soon]
                </Select.Option>
                <Select.Option value="kimi-k3-remote" disabled>
                  Kimi K3 (Remote) [Coming Soon]
                </Select.Option>
                <Select.Option value="openai-remote" disabled>
                  OpenAI (Remote) [Coming Soon]
                </Select.Option>
                <Select.Option value="claude-remote" disabled>
                  Claude (Remote) [Coming Soon]
                </Select.Option>
                <Select.Option value="grok-remote" disabled>
                  Grok (Remote) [Coming Soon]
                </Select.Option>
              </Select>
            )}
          </Form.Item>
          <Form.Item label="API Key">
            {loading ? (
              <Skeleton title={{ width: 300 }} paragraph={false} active />
            ) : (
              <Input.Password
                value={values.ai_token || ""}
                onChange={(e) => onChange({ ai_token: e.target.value })}
                placeholder="Xyz...qW1 (Optional)"
              />
            )}
          </Form.Item>
          {values.ai_enabled && values.ai_type.endsWith("-remote") && (
            <Form.Item label="API Host">
              {loading ? (
                <Skeleton title={{ width: 300 }} paragraph={false} active />
              ) : (
                <Input
                  value={values.ai_host || ""}
                  onChange={(e) => onChange({ ai_host: (e.target.value || "").replace(/\/+$/, "") })}
                  placeholder="https://api.example.com (Optional)"
                />
              )}
            </Form.Item>
          )}
        </>
      )}
    </DynamicComponent>
  );
}

AIFormSettings.propTypes = SettingsEditorPropTypes;

AIFormSettings.defaultProps = SettingsEditorDefaultProps;
