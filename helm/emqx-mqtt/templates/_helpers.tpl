{{- define "kubectl" -}}
{{- /* image for kubectl matching server's - pass .Capabilities.KubeVersion */ -}}
bitnami/kubectl:{{ .Major }}.{{ trimSuffix "+" .Minor  -}}
{{- end -}}