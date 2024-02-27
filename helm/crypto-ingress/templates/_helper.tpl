{{- define "crypto-ingress.env" -}}
- name: ENVIRONMENT
  value: {{ .Values.environment | quote }}
- name: INFLUXDB_HOST
  value: {{ .Values.influx.host | quote }}
- name: INFLUXDB_TOKEN
  value: {{ .Values.influx.token | quote }}
- name: MQTT_PASSWORD
  value: {{ .Values.mqtt.password | quote }}
- name: DEBUG
  value: {{ .Values.cryptoIngress.debug | quote }}
- name: SENTRY_DSN
  value: {{ .Values.cryptoIngress.monitoring.sentryDSN | default "" }}
- name: KRAKEN_KEY
  value: {{ .Values.kraken.key | default "" }}
- name: KRAKEN_SECRET
  value: {{ .Values.kraken.secret | default "" }}
{{- end -}}
