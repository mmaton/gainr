{{- define "crypto-ingress.env" -}}
- name: INFLUXDB_HOST
  value: {{ .Values.influx.host | quote }}
- name: INFLUXDB_TOKEN
  value: {{ .Values.influx.token | quote }}
{{- end -}}