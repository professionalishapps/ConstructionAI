"""Agent 9: Progress Analyzer (Drone/Photo Analysis)

Verifies completion percentage using computer vision on site photos.
For MVP: Simulates CV analysis with synthetic data. Can be enhanced with OpenCV/YOLO later.
"""
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import random


def simulate_visual_progress_assessment(
    photo_count: int,
    activity_type: str,
    reported_completion_pct: float
) -> Tuple[float, str]:
    """Simulate computer vision assessment of progress from photos.
    
    In production, this would use OpenCV/YOLO to analyze actual site photos.
    For MVP, generates realistic assessments based on activity type.
    
    Args:
        photo_count: Number of site photos analyzed
        activity_type: Type of construction activity
        reported_completion_pct: Self-reported completion percentage
    
    Returns:
        Tuple of (visual_completion_pct, confidence_level)
    """
    if photo_count == 0:
        return reported_completion_pct, "No photos available"
    
    # Simulate variance based on activity visibility
    visibility_variance = {
        'excavation': 3.0,  # Easy to see
        'foundation': 4.0,
        'framing': 3.0,
        'roofing': 2.5,
        'exterior_finish': 3.5,
        'mep': 8.0,  # Hard to see (inside walls)
        'drywall': 5.0,
        'interior_finish': 6.0,
        'painting': 4.0
    }
    
    variance = visibility_variance.get(activity_type.lower(), 5.0)
    
    # Simulate CV assessment with some variance
    # In reality, this would analyze actual images
    visual_assessment = reported_completion_pct + random.uniform(-variance, variance)
    visual_assessment = max(0, min(100, visual_assessment))
    
    # Confidence based on photo count and activity type
    if photo_count >= 10:
        confidence = "High"
    elif photo_count >= 5:
        confidence = "Medium"
    else:
        confidence = "Low"
    
    return round(visual_assessment, 1), confidence


def detect_progress_discrepancy(
    visual_assessment: float,
    reported_completion: float,
    tolerance_pct: float = 5.0
) -> Tuple[bool, float, str]:
    """Detect discrepancies between visual and reported progress.
    
    Args:
        visual_assessment: Visually assessed completion %
        reported_completion: Reported completion %
        tolerance_pct: Acceptable variance percentage
    
    Returns:
        Tuple of (discrepancy_detected, variance, status)
    """
    variance = reported_completion - visual_assessment
    abs_variance = abs(variance)
    
    discrepancy_detected = abs_variance > tolerance_pct
    
    if not discrepancy_detected:
        status = "Verified - Progress aligns with visual assessment"
    elif variance > 0:
        status = f"Over-reporting suspected - {abs_variance:.1f}% discrepancy"
    else:
        status = f"Under-reporting detected - {abs_variance:.1f}% discrepancy"
    
    return discrepancy_detected, round(variance, 1), status


def analyze_activity_completion(
    activities: List[Dict[str, any]]
) -> Dict[str, any]:
    """Analyze completion status across multiple activities.
    
    Args:
        activities: List of activity dicts with 'name', 'reported_pct', 
                   'visual_pct', 'critical_path'
    
    Returns:
        Dict with activity analysis
    """
    if not activities:
        return {
            'total_activities': 0,
            'verified': 0,
            'discrepancies': 0,
            'critical_path_issues': []
        }
    
    verified_count = 0
    discrepancy_count = 0
    critical_path_issues = []
    total_reported = 0
    total_visual = 0
    
    for activity in activities:
        name = activity.get('name', 'Unknown')
        reported = activity.get('reported_pct', 0)
        visual = activity.get('visual_pct', 0)
        critical = activity.get('critical_path', False)
        
        total_reported += reported
        total_visual += visual
        
        discrepancy_detected, variance, _ = detect_progress_discrepancy(visual, reported)
        
        if discrepancy_detected:
            discrepancy_count += 1
            if critical and variance > 0:  # Over-reporting on critical path
                critical_path_issues.append({
                    'activity': name,
                    'variance': variance,
                    'impact': 'High - affects schedule forecast'
                })
        else:
            verified_count += 1
    
    avg_reported = total_reported / len(activities)
    avg_visual = total_visual / len(activities)
    
    return {
        'total_activities': len(activities),
        'verified': verified_count,
        'discrepancies': discrepancy_count,
        'verification_rate': round((verified_count / len(activities)) * 100, 1),
        'avg_reported_completion': round(avg_reported, 1),
        'avg_visual_completion': round(avg_visual, 1),
        'overall_variance': round(avg_reported - avg_visual, 1),
        'critical_path_issues': critical_path_issues
    }


def generate_visual_progress_report(
    overall_completion: float,
    visual_assessment: float,
    photo_analysis: Dict[str, any],
    discrepancy_detected: bool
) -> Dict[str, any]:
    """Generate comprehensive visual progress report.
    
    Args:
        overall_completion: Overall reported project completion
        visual_assessment: Visual assessment of completion
        photo_analysis: Dict with photo analysis details
        discrepancy_detected: Whether significant discrepancy found
    
    Returns:
        Dict with progress report
    """
    variance = overall_completion - visual_assessment
    
    if discrepancy_detected:
        if variance > 0:
            finding = "Progress over-reporting detected"
            recommendation = "Adjust schedule forecasts based on visual assessment"
            risk_level = "MEDIUM" if variance < 10 else "HIGH"
        else:
            finding = "Progress under-reporting detected"
            recommendation = "Verify reporting accuracy and update forecasts"
            risk_level = "LOW"
    else:
        finding = "Progress reporting verified"
        recommendation = "Continue current progress tracking methods"
        risk_level = "LOW"
    
    return {
        'reported_completion': round(overall_completion, 1),
        'visual_completion': round(visual_assessment, 1),
        'variance': round(variance, 1),
        'variance_pct': round((variance / overall_completion * 100) if overall_completion > 0 else 0, 1),
        'finding': finding,
        'recommendation': recommendation,
        'risk_level': risk_level,
        'photo_count': photo_analysis.get('photo_count', 0),
        'analysis_confidence': photo_analysis.get('confidence', 'Unknown')
    }


def recommend_photo_documentation_improvements(
    photo_count: int,
    activities_count: int,
    discrepancy_rate: float
) -> List[str]:
    """Recommend improvements to photo documentation practices.
    
    Args:
        photo_count: Current number of photos
        activities_count: Number of activities being tracked
        discrepancy_rate: Rate of discrepancies detected (%)
    
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Photo coverage
    photos_per_activity = photo_count / activities_count if activities_count > 0 else 0
    
    if photos_per_activity < 2:
        recommendations.append("Increase photo documentation frequency (target: 2-3 photos per activity)")
    elif photos_per_activity < 5:
        recommendations.append("Photo coverage is adequate, consider slight increase for better accuracy")
    else:
        recommendations.append("Photo documentation coverage is good")
    
    # Discrepancy-based recommendations
    if discrepancy_rate > 20:
        recommendations.extend([
            "High discrepancy rate detected - implement mandatory photo verification",
            "Provide training on accurate progress assessment",
            "Consider third-party progress verification"
        ])
    elif discrepancy_rate > 10:
        recommendations.extend([
            "Moderate discrepancies detected - increase spot-check frequency",
            "Review progress reporting procedures"
        ])
    
    # Best practices
    recommendations.extend([
        "Use consistent photo angles for progress comparison",
        "Include reference markers in photos for scale",
        "Time-stamp and geo-tag all progress photos",
        "Maintain organized photo library by activity and date"
    ])
    
    # Technology recommendations
    if activities_count > 10:
        recommendations.extend([
            "Consider drone photography for large areas",
            "Evaluate 360° camera systems for comprehensive coverage",
            "Explore AI-powered progress tracking tools"
        ])
    
    return recommendations


def calculate_progress_verification_risk(
    discrepancy_rate: float,
    avg_variance: float,
    critical_path_issues: int,
    photo_coverage: float
) -> Tuple[int, str]:
    """Calculate risk score for progress verification.
    
    Args:
        discrepancy_rate: Percentage of activities with discrepancies
        avg_variance: Average variance in percentage points
        critical_path_issues: Number of critical path activities with issues
        photo_coverage: Photo coverage adequacy (0-100)
    
    Returns:
        Tuple of (risk_score 0-100, risk_level)
    """
    risk_score = 0
    
    # Discrepancy rate (0-35 points)
    risk_score += min(35, discrepancy_rate * 0.35)
    
    # Variance magnitude (0-30 points)
    risk_score += min(30, abs(avg_variance) * 3)
    
    # Critical path impact (0-25 points)
    risk_score += min(25, critical_path_issues * 12.5)
    
    # Photo coverage (0-10 points, inverted)
    coverage_risk = (100 - photo_coverage) * 0.1
    risk_score += min(10, coverage_risk)
    
    risk_score = min(100, max(0, risk_score))
    
    if risk_score < 30:
        risk_level = "LOW"
    elif risk_score < 60:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
    
    return int(risk_score), risk_level


if __name__ == "__main__":
    # Quick test
    print("=== Progress Analyzer Test ===\n")
    
    # Simulate visual assessment
    visual_pct, confidence = simulate_visual_progress_assessment(
        photo_count=8,
        activity_type="framing",
        reported_completion_pct=75.0
    )
    print(f"Visual Assessment: {visual_pct}% (Confidence: {confidence})\n")
    
    # Detect discrepancy
    discrepancy, variance, status = detect_progress_discrepancy(
        visual_assessment=visual_pct,
        reported_completion=75.0
    )
    print(f"Discrepancy Detected: {discrepancy}")
    print(f"Variance: {variance}%")
    print(f"Status: {status}\n")
    
    # Activity analysis
    activities = [
        {'name': 'Framing', 'reported_pct': 75, 'visual_pct': 72, 'critical_path': True},
        {'name': 'Roofing', 'reported_pct': 60, 'visual_pct': 58, 'critical_path': False},
        {'name': 'Windows', 'reported_pct': 80, 'visual_pct': 75, 'critical_path': True},
    ]
    
    analysis = analyze_activity_completion(activities)
    print(f"Activity Analysis:")
    print(f"  Verified: {analysis['verified']}/{analysis['total_activities']}")
    print(f"  Verification Rate: {analysis['verification_rate']}%")
    print(f"  Overall Variance: {analysis['overall_variance']}%\n")
    
    # Risk score
    risk_score, risk_level = calculate_progress_verification_risk(
        discrepancy_rate=33.3,
        avg_variance=analysis['overall_variance'],
        critical_path_issues=len(analysis['critical_path_issues']),
        photo_coverage=65
    )
    print(f"Progress Verification Risk: {risk_score} - {risk_level}")

