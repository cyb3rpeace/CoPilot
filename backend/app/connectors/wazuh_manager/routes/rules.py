from typing import List
from fastapi import APIRouter, HTTPException, Security, Depends
from starlette.status import HTTP_401_UNAUTHORIZED
from loguru import logger

# App specific imports
from app.auth.routes.auth import auth_handler
from app.db.db_session import session
from app.connectors.wazuh_manager.schema.rules import (
    RuleDisable, RuleDisableResponse, RuleEnableResponse, RuleEnable, AllDisabledRuleResponse
)
from app.connectors.wazuh_manager.models.rules import DisabledRule
from app.connectors.wazuh_manager.services.rules import disable_rule, enable_rule

NEW_LEVEL = "1"
wazuh_manager_router = APIRouter()

def verify_admin(user):
    if not user.is_admin:
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED, detail="Unauthorized")

def query_disabled_rule(rule_id: str):
    return session.query(DisabledRule).filter(DisabledRule.rule_id == rule_id).first()

@wazuh_manager_router.get("/rule/disabled", response_model=AllDisabledRuleResponse, description="Get all disabled rules")
async def get_disabled_rules(user=Depends(auth_handler.get_current_user)) -> AllDisabledRuleResponse:
    logger.info(f"Fetching all disabled rules for user: {user.username}")
    verify_admin(user)
    disabled_rules = session.query(DisabledRule).all()
    return AllDisabledRuleResponse(
        disabled_rules=disabled_rules,
        success=True,
        message="Successfully fetched all disabled rules"
    )

@wazuh_manager_router.post("/rule/disable", response_model=RuleDisableResponse, description="Disable a Wazuh Rule")
async def disable_wazuh_rule(rule: RuleDisable, user=Depends(auth_handler.get_current_user)) -> RuleDisableResponse:
    logger.info(f"Disabling rule for user: {user.username}")
    verify_admin(user)

    if query_disabled_rule(rule.rule_id):
        raise HTTPException(status_code=404, detail="Rule is already disabled")

    rule_disabled = disable_rule(rule)
    if rule_disabled:
        new_disabled_rule = DisabledRule(
            rule_id=rule.rule_id,
            previous_level=rule_disabled.previous_level,
            new_level=NEW_LEVEL,
            reason_for_disabling=rule.reason_for_disabling,
            length_of_time=rule.length_of_time,
            disabled_by=user.username
        )
        session.add(new_disabled_rule)
        session.commit()
        return rule_disabled
    else:
        raise HTTPException(status_code=404, detail="Was not able to disable rule")

@wazuh_manager_router.post("/rule/enable", response_model=RuleEnableResponse, description="Enable a Wazuh Rule")
async def enable_wazuh_rule(rule: RuleEnable, user=Depends(auth_handler.get_current_user)) -> RuleEnableResponse:
    logger.info(f"Enabling rule for user: {user.username}")
    verify_admin(user)

    disabled_rule = query_disabled_rule(rule.rule_id)
    if not disabled_rule:
        raise HTTPException(status_code=404, detail="Rule is already enabled")

    previous_level = disabled_rule.previous_level
    rule_enabled = enable_rule(rule, previous_level)

    if rule_enabled:
        session.delete(disabled_rule)
        session.commit()
        return rule_enabled
    else:
        raise HTTPException(status_code=404, detail="Was not able to enable rule")