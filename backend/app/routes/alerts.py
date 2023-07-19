from flask import Blueprint
from flask import jsonify
from flask import request

from app.services.WazuhIndexer.alerts import AlertsService

bp = Blueprint("alerts", __name__)


@bp.route("/alerts", methods=["GET"])
def get_alerts() -> jsonify:
    """
    Retrieves all alerts from the AlertsService.

    This endpoint retrieves all available alerts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts` method. The result is a list of all alerts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of alerts. Each item in the list is a dictionary representing an alert,
        containing all its associated data.
    """
    service = AlertsService()
    alerts = service.collect_alerts(size=1000)  # replace `collect_all_alerts` with `collect_alerts(size=1000)`
    return jsonify(alerts)


@bp.route("/alerts/<agent_name>", methods=["GET"])
def get_alerts_by_agent(agent_name: str) -> jsonify:
    """
    Retrieves all alerts from the AlertsService by agent name.

    This endpoint retrieves all available alerts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_agent` method. The result is a list of all alerts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of alerts. Each item in the list is a dictionary representing an alert,
        containing all its associated data.
    """
    service = AlertsService()
    alerts = service.collect_alerts_by_agent_name(agent_name=agent_name)
    return jsonify(alerts)


@bp.route("/alerts/last_24_hours", methods=["GET"])
def get_alerts_last_24_hours() -> jsonify:
    """
    Retrieves all alerts from all wazuh indices with the last 24 hours.

    This endpoint retrieves all available alerts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_agent` method. The result is a list of all alerts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of alerts. Each item in the list is a dictionary representing an alert,
        containing all its associated data.
    """
    service = AlertsService()
    alerts = service.collect_alerts_last_24_hours(size=1000)
    return jsonify(alerts)


@bp.route("/alerts/top_10", methods=["GET"])
def get_top_10_alerts() -> jsonify:
    """
    Retrieves top 10 alerts from the AlertsService per index.

    This endpoint retrieves top 10 alerts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts` method. The result is a list of top 10 alerts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of alerts. Each item in the list is a dictionary representing an alert,
        containing all its associated data.
    """
    service = AlertsService()
    alerts = service.collect_alerts(size=10)  # replace `collect_top_10_alerts` with `collect_alerts(size=10)`
    return jsonify(alerts)


@bp.route("/alerts/index/<index_name>", methods=["GET"])
def get_alerts_by_index(index_name: str) -> jsonify:
    """
    Retrieves all alerts from the AlertsService by index name.

    This endpoint retrieves all available alerts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_index` method. The result is a list of all alerts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of alerts. Each item in the list is a dictionary representing an alert,
        containing all its associated data.
    """
    service = AlertsService()
    alerts = service.collect_alerts_by_index(index_name=index_name, size=1000)
    return jsonify(alerts)


@bp.route("/alerts/hosts", methods=["GET"])
def get_hosts() -> jsonify:
    """
    Retrieves all hosts from the AlertsService that have an alert.

    This endpoint retrieves all available hosts from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_host` method. The result is a list of all hosts currently
    available.

    Returns:
        jsonify: A JSON response containing a list of hosts. Each item in the list is a dictionary representing a host,
        containing all its associated data.
    """
    service = AlertsService()
    hosts = service.collect_alerts_by_host()
    return jsonify(hosts)


@bp.route("/alerts/rules", methods=["GET"])
def get_rules() -> jsonify:
    """
    Retrieves all rules from the AlertsService that have an alert.

    This endpoint retrieves all available rules from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_rule` method. The result is a list of all rules currently
    available.

    Returns:
        jsonify: A JSON response containing a list of rules. Each item in the list is a dictionary representing a rule,
        containing all its associated data.
    """
    service = AlertsService()
    rules = service.collect_alerts_by_rule()
    return jsonify(rules)


@bp.route("/alerts/rules/host", methods=["GET"])
def get_rules_by_host() -> jsonify:
    """
    Retrieves all rules from the AlertsService that have an alert and organizes by host.

    This endpoint retrieves all available rules from the AlertsService. It does this by creating an instance of
    the AlertsService class and calling its `collect_alerts_by_rule_per_host` method. The result is a list of all rules currently
    available.

    Returns:
        jsonify: A JSON response containing a list of rules. Each item in the list is a dictionary representing a rule,
        containing all its associated data.
    """
    service = AlertsService()
    rules = service.collect_alerts_by_rule_per_host()
    return jsonify(rules)


@bp.route("/alerts/escalate", methods=["POST"])
def escalate_alert() -> jsonify:
    """
    Accepts a POST request with an alert_uid and esacalates the alert by creating an alert in DFIR-IRIS

    This endpoint accepts a POST request with an alert_uid and esacalates the alert by creating an alert in DFIR-IRIS.

    Returns:
        jsonify: A JSON response containing the status of the escalation.
    """
    service = AlertsService()
    alert_id = request.json["alert_id"]
    index = request.json["index"]
    status = service.escalate_alert(alert_id=alert_id, index=index)
    return jsonify(status)
