# smart_common/providers/wizard/engine.py
from __future__ import annotations
import logging
from typing import Any, Mapping

from pydantic import BaseModel, ValidationError
from smart_common.providers.wizard.exceptions import WizardSessionStateError
from smart_common.providers.enums import ProviderVendor
from smart_common.providers.wizard.exceptions import (
    WizardNotConfiguredError,
    WizardResultError,
    WizardSessionExpiredError,
    WizardStepNotFoundError,
)
from smart_common.providers.wizard.store import WizardSessionStore


logger = logging.getLogger(__name__)

ProviderDefinitions = Mapping[str, Any]


class WizardEngine:
    """
    Coordinates provider wizard execution.

    CONTRACT (IMPORTANT):
    - `step`     -> step user MUST FILL NOW
    - `schema`   -> schema for THIS step
    - `options`  -> options for THIS step
    """

    def __init__(
        self,
        provider_definitions: Mapping[ProviderVendor, ProviderDefinitions],
        session_store: WizardSessionStore | None = None,
    ) -> None:
        self._definitions = provider_definitions
        self._session_store = session_store or WizardSessionStore()

    def run_step(
        self,
        vendor: ProviderVendor,
        step_name: str,
        payload: Mapping[str, Any] | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute single wizard step.
        """
        logger.info(
            "Wizard step start",
            extra={
                "vendor": vendor.value,
                "step": step_name,
                "context": dict(context or {}),
            },
        )

        # ------------------------------------------------------------------
        # Resolve provider + wizard
        # ------------------------------------------------------------------
        meta = self._definitions.get(vendor)
        if not meta or not (wizard := meta.get("wizard")):
            raise WizardNotConfiguredError(
                f"No wizard declared for provider {vendor.value}"
            )

        step_definition = wizard.get(step_name)
        if not step_definition:
            raise WizardStepNotFoundError(
                f"Step '{step_name}' is not available for provider {vendor.value}"
            )

        # ------------------------------------------------------------------
        # Resolve wizard session
        # ------------------------------------------------------------------
        session = self._resolve_session(
            vendor=vendor,
            context=context or {},
            step_name=step_name,
        )

        # ------------------------------------------------------------------
        # Validate payload against CURRENT step schema
        # ------------------------------------------------------------------
        model = self._validate_payload(step_definition.schema, payload or {})

        # ------------------------------------------------------------------
        # Execute step handler
        # ------------------------------------------------------------------
        result: dict[str, Any] = (
            step_definition.handler(model, session.session_data) or {}
        )

        # ------------------------------------------------------------------
        # Merge session updates
        # ------------------------------------------------------------------
        session.session_data.update(result.get("session_updates", {}))
        session.context = {**session.context, **dict(result.get("context", {}))}
        session.context["wizard_session_id"] = session.id
        session.last_step = step_name

        self._session_store.persist(session)

        # ------------------------------------------------------------------
        # Completion
        # ------------------------------------------------------------------
        is_complete = bool(result.get("is_complete")) or bool(
            result.get("final_config")
        )
        final_config = result.get("final_config")

        if is_complete:
            if result.get("next_step"):
                raise WizardResultError(
                    "Wizard cannot report completion while next_step is set"
                )

            config_schema = meta.get("config_schema")
            if final_config and config_schema:
                final_config = config_schema.model_validate(final_config).model_dump()

            return {
                "vendor": vendor,
                "step": None,
                "schema": None,
                "options": {},
                "context": dict(session.context),
                "is_complete": True,
                "final_config": final_config,
            }

        # ------------------------------------------------------------------
        # Resolve NEXT step (THIS is what user fills now)
        # ------------------------------------------------------------------
        next_step = result.get("next_step")
        if not next_step:
            raise WizardResultError(
                "Wizard step must define next_step or set is_complete=True"
            )

        next_definition = wizard.get(next_step)
        if not next_definition:
            raise WizardStepNotFoundError(
                f"Next step '{next_step}' not found for provider {vendor.value}"
            )

        # ------------------------------------------------------------------
        # FINAL RESPONSE (CORRECT CONTRACT)
        # ------------------------------------------------------------------

        logger.info(
            "Wizard step completed",
            extra={
                "vendor": vendor.value,
                "step": step_name,
                "is_complete": is_complete,
            },
        )

        return {
            "vendor": vendor,
            "step": next_step,  # ✅ CURRENT STEP
            "schema": next_definition.schema.model_json_schema(),  # ✅ CURRENT SCHEMA
            "options": dict(result.get("options", {})),  # ✅ OPTIONS FOR STEP
            "context": dict(session.context),
            "is_complete": False,
            "final_config": None,
        }

    # ------------------------------------------------------------------
    # Session resolution
    # ------------------------------------------------------------------
    def _resolve_session(
        self,
        vendor: ProviderVendor,
        context: Mapping[str, Any],
        *,
        step_name: str,
    ):
        session_id = context.get("wizard_session_id")

        if not session_id:
            if step_name == "auth":
                return self._session_store.create(vendor)

            raise WizardSessionExpiredError(
                "wizard_session_id is required for this step"
            )

        session = self._session_store.get(str(session_id))
        if not session:
            raise WizardSessionExpiredError("Wizard session has expired, start again")

        if session.vendor != vendor:
            raise WizardNotConfiguredError("Wizard session vendor mismatch")

        return session

    # ------------------------------------------------------------------
    # Payload validation
    # ------------------------------------------------------------------
    def _validate_payload(
        self,
        schema: type[BaseModel],
        payload: Mapping[str, Any],
    ) -> BaseModel:
        try:
            return schema.model_validate(payload)
        except ValidationError as exc:
            logger.warning(
                "Wizard payload validation failed",
                extra={
                    "schema": schema.__name__,
                    "errors": exc.errors(),
                },
            )
            raise WizardSessionStateError("Invalid payload for wizard step") from exc
