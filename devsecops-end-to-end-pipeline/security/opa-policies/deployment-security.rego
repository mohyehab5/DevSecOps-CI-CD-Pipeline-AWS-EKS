package main

# Deny any Deployment that doesn't run as non-root
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.securityContext.runAsNonRoot == true
    msg := sprintf("Container '%s' must set securityContext.runAsNonRoot = true", [container.name])
}

# Deny any container without CPU/memory limits (prevents noisy-neighbor / DoS risk)
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    not container.resources.limits
    msg := sprintf("Container '%s' must define resource limits", [container.name])
}

# Deny any container that allows privilege escalation
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    container.securityContext.allowPrivilegeEscalation == true
    msg := sprintf("Container '%s' must not allow privilege escalation", [container.name])
}

# Deny use of the 'latest' image tag — breaks reproducibility and image scanning history
deny[msg] {
    input.kind == "Deployment"
    container := input.spec.template.spec.containers[_]
    endswith(container.image, ":latest")
    msg := sprintf("Container '%s' must not use the ':latest' tag", [container.name])
}
