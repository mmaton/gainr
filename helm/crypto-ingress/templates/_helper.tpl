{{- define "crypto-ingress.env" -}}
- name: INFLUXDB_HOST
  value: {{ .Values.influx.host | quote }}
- name: INFLUXDB_TOKEN
  value: {{ .Values.influx.token | quote }}
- name: MQTT_PASSWORD
  value: {{ .Values.cryptoIngress.mqtt.password | quote }}
- name: DEBUG
  value: {{ .Values.cryptoIngress.debug | quote }}
- name: SENTRY_DSN
  value: {{ .Values.cryptoIngress.monitoring.sentryDSN | default "" }}
{{- end -}}
