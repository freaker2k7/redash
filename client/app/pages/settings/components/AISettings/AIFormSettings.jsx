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

  const models = {
    "huggingface-local": {
      name: "HuggingFace (Local)",
      options: [],
      enabled: true,
    },
    "huggingface-remote": {
      name: "HuggingFace (Remote) [Coming Soon]",
      options: [],
    },
    "kimi-k3-remote": {
      name: "Kimi K3 (Remote) [Coming Soon]",
      options: [],
    },
    "ollama-remote": {
      name: "Ollama (Remote)",
      options: [
        { value: "gemma3", label: "Gemma 3" },
        { value: "llama2-7b-chat", label: "LLaMA 2 7B Chat" },
        { value: "llama2-13b-chat", label: "LLaMA 2 13B Chat" },
      ],
      enabled: true,
    },
    "openai-cloud": {
      name: "OpenAI (Cloud) [Coming Soon]",
      options: [
        { value: "gpt-5.6", label: "GPT-5.6" },
        { value: "gpt-5.5", label: "GPT-5.5" },
        { value: "gpt-5.4", label: "GPT-5.4" },
        { value: "gpt-5", label: "GPT-5" },
        { value: "gpt-4", label: "GPT-4" },
        { value: "gpt-4-32k", label: "GPT-4 32K" },
        { value: "gpt-3.5-turbo", label: "GPT-3.5 Turbo" },
      ],
    },
    "claude-cloud": {
      name: "Claude (Cloud) [Coming Soon]",
      options: [
        { value: "claude-5", label: "Claude 5" },
        { value: "claude-4", label: "Claude 4" },
        { value: "claude-3", label: "Claude 3" },
        { value: "claude-2", label: "Claude 2" },
        { value: "claude-instant", label: "Claude Instant" },
      ],
    },
    "grok-cloud": {
      name: "Grok (Cloud) [Coming Soon]",
      options: [
        { value: "grok-4", label: "Grok 4" },
        { value: "grok-3", label: "Grok 3" },
        { value: "grok-2", label: "Grok 2" },
        { value: "grok-1", label: "Grok 1" },
      ],
    },
  };

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
                {Object.entries(models).map(([key, model]) => (
                  <Select.Option key={key} value={key} disabled={!model.enabled}>
                    {model.name}
                  </Select.Option>
                ))}
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
          {values.ai_enabled && (values.ai_type.endsWith("-remote") || values.ai_type.endsWith("-cloud")) && (
            <Form.Item label="API Host">
              {loading ? (
                <Skeleton title={{ width: 300 }} paragraph={false} active />
              ) : (
                <Input
                  value={values.ai_host || ""}
                  onChange={(e) => onChange({ ai_host: (e.target.value || "").replace(/\/+$/, "") })}
                  placeholder={
                    "https://api.example.com " + (values.ai_type.endsWith("-cloud") ? "[Required]" : "(Optional)")
                  }
                  required={values.ai_type.endsWith("-cloud")}
                />
              )}
            </Form.Item>
          )}
          {Object.entries(models).map(
            ([key, model]) =>
              values.ai_enabled &&
              values.ai_type === key &&
              model.options.length > 0 && (
                <Form.Item label="Model Name" key={key}>
                  {loading ? (
                    <Skeleton title={{ width: 300 }} paragraph={false} active />
                  ) : (
                    <Select
                      value={values.ai_model || model.options[0].value}
                      onChange={(value) => onChange({ ai_model: value })}
                    >
                      {model.options.map((option) => (
                        <Select.Option key={option.value} value={option.value}>
                          {option.label}
                        </Select.Option>
                      ))}
                    </Select>
                  )}
                </Form.Item>
              )
          )}
        </>
      )}
    </DynamicComponent>
  );
}

AIFormSettings.propTypes = SettingsEditorPropTypes;

AIFormSettings.defaultProps = SettingsEditorDefaultProps;
