from flask import Blueprint, jsonify


header_analysis_bp = Blueprint('header_analysis', __name__)

@header_analysis_bp.route('/header_analysis', methods=["POST"])
def header_analysis_mxtool():
    pass