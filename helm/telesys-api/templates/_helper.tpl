{{- define "telesys-api.env" -}}
- name: ENVIRONMENT
  value: {{ .Values.environment | quote }}
- name: INFLUXDB_HOST
  value: {{ .Values.influx.host | quote }}
- name: INFLUXDB_TOKEN
  value: {{ .Values.influx.token | quote }}
- name: MQTT_PASSWORD
  value: {{ .Values.mqtt.password | quote }}
- name: DEBUG
  value: {{ .Values.telesysAPI.debug | quote }}
- name: SENTRY_DSN
  value: {{ .Values.telesysAPI.monitoring.sentryDSN | quote }}
{{- end -}}
