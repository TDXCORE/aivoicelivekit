#!/usr/bin/env python3
"""
Twilio Call Logs Analyzer

This script retrieves comprehensive information about a Twilio call including:
- Call details and status
- Events and timeline
- Recordings if any
- SIP logs and debug information
- Conference details if applicable
- All available metadata

Usage:
    python get_call_logs.py --call-sid CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
    python get_call_logs.py --call-sid CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx --detailed
"""

import argparse
import json
from datetime import datetime
from twilio.rest import Client
from dotenv import load_dotenv
import os
import logging

# Load environment variables
load_dotenv('.env.test')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TwilioCallAnalyzer:
    def __init__(self):
        self.account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        self.auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        
        if not all([self.account_sid, self.auth_token]):
            raise ValueError("Missing Twilio credentials in .env.test")
        
        self.client = Client(self.account_sid, self.auth_token)

    def get_call_details(self, call_sid: str) -> dict:
        """Get basic call details"""
        try:
            call = self.client.calls(call_sid).fetch()
            
            return {
                "sid": call.sid,
                "account_sid": call.account_sid,
                "from": call.from_formatted,
                "to": call.to_formatted,
                "status": call.status,
                "start_time": str(call.start_time) if call.start_time else None,
                "end_time": str(call.end_time) if call.end_time else None,
                "duration": call.duration,
                "price": call.price,
                "price_unit": call.price_unit,
                "direction": call.direction,
                "answered_by": call.answered_by,
                "caller_name": call.caller_name,
                "uri": call.uri,
                "parent_call_sid": call.parent_call_sid,
                "phone_number_sid": call.phone_number_sid,
                "forwarded_from": call.forwarded_from,
                "group_sid": call.group_sid,
                "queue_time": call.queue_time,
                "trunk_sid": call.trunk_sid
            }
        except Exception as e:
            logger.error(f"Error fetching call details: {e}")
            return None

    def get_call_events(self, call_sid: str) -> list:
        """Get call events/timeline"""
        try:
            events = self.client.calls(call_sid).events.list()
            
            event_list = []
            for event in events:
                event_list.append({
                    "timestamp": str(event.timestamp),
                    "event_type": event.name,
                    "data": event.data
                })
            
            return sorted(event_list, key=lambda x: x["timestamp"])
        except Exception as e:
            logger.error(f"Error fetching call events: {e}")
            return []

    def get_call_recordings(self, call_sid: str) -> list:
        """Get call recordings"""
        try:
            recordings = self.client.recordings.list(call_sid=call_sid)
            
            recording_list = []
            for recording in recordings:
                recording_list.append({
                    "sid": recording.sid,
                    "account_sid": recording.account_sid,
                    "call_sid": recording.call_sid,
                    "status": recording.status,
                    "duration": recording.duration,
                    "channels": recording.channels,
                    "source": recording.source,
                    "price": recording.price,
                    "uri": recording.uri,
                    "encryption_details": recording.encryption_details,
                    "date_created": str(recording.date_created),
                    "date_updated": str(recording.date_updated)
                })
            
            return recording_list
        except Exception as e:
            logger.error(f"Error fetching recordings: {e}")
            return []

    def get_call_notifications(self, call_sid: str) -> list:
        """Get call notifications/alerts"""
        try:
            notifications = self.client.calls(call_sid).notifications.list()
            
            notification_list = []
            for notification in notifications:
                notification_list.append({
                    "sid": notification.sid,
                    "account_sid": notification.account_sid,
                    "call_sid": notification.call_sid,
                    "log": notification.log,
                    "error_code": notification.error_code,
                    "more_info": notification.more_info,
                    "message_text": notification.message_text,
                    "message_date": str(notification.message_date),
                    "request_url": notification.request_url,
                    "request_method": notification.request_method,
                    "request_variables": notification.request_variables,
                    "response_headers": notification.response_headers,
                    "response_body": notification.response_body
                })
            
            return notification_list
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []

    def get_call_feedback(self, call_sid: str) -> dict:
        """Get call quality feedback if available"""
        try:
            feedback = self.client.calls(call_sid).feedback.fetch()
            
            return {
                "account_sid": feedback.account_sid,
                "call_sid": feedback.call_sid,
                "quality_score": feedback.quality_score,
                "issues": feedback.issues,
                "date_created": str(feedback.date_created),
                "date_updated": str(feedback.date_updated)
            }
        except Exception as e:
            # Feedback might not exist for all calls
            logger.debug(f"No feedback found for call: {e}")
            return None

    def get_call_summary(self, call_sid: str) -> dict:
        """Get call summary with metrics"""
        try:
            summary = self.client.calls(call_sid).summary().fetch()
            
            return {
                "account_sid": summary.account_sid,
                "call_sid": summary.call_sid,
                "call_type": summary.call_type,
                "call_state": summary.call_state,
                "answered_by": summary.answered_by,
                "connectivity_issue_percentage": summary.connectivity_issue_percentage,
                "quality_issues": summary.quality_issues,
                "carrier": summary.carrier,
                "handset": summary.handset,
                "processing_state": summary.processing_state,
                "created_time": str(summary.created_time),
                "start_time": str(summary.start_time),
                "end_time": str(summary.end_time)
            }
        except Exception as e:
            logger.debug(f"No summary found for call: {e}")
            return None

    def get_sip_logs(self, call_sid: str) -> list:
        """Get SIP logs for trunk calls"""
        try:
            # Try to get SIP interface logs
            sip_logs = []
            
            # Get the call details first to check if it's a SIP trunk call
            call = self.client.calls(call_sid).fetch()
            
            if call.trunk_sid:
                logger.info(f"Call used SIP trunk: {call.trunk_sid}")
                # You can add more SIP-specific log retrieval here
                # Twilio's SIP logs are usually available through the console
                # but not always through the API
            
            return sip_logs
        except Exception as e:
            logger.error(f"Error fetching SIP logs: {e}")
            return []

    def analyze_call(self, call_sid: str, detailed: bool = False) -> dict:
        """Perform comprehensive call analysis"""
        logger.info(f"Analyzing call: {call_sid}")
        
        analysis = {
            "call_sid": call_sid,
            "analysis_timestamp": datetime.now().isoformat(),
            "call_details": None,
            "events": [],
            "recordings": [],
            "notifications": [],
            "feedback": None,
            "summary": None,
            "sip_info": []
        }
        
        # Get basic call details
        logger.info("Fetching call details...")
        analysis["call_details"] = self.get_call_details(call_sid)
        
        if not analysis["call_details"]:
            logger.error("Call not found or access denied")
            return analysis
        
        # Get call events
        logger.info("Fetching call events...")
        analysis["events"] = self.get_call_events(call_sid)
        
        # Get recordings
        logger.info("Fetching recordings...")
        analysis["recordings"] = self.get_call_recordings(call_sid)
        
        # Get notifications/errors
        logger.info("Fetching notifications...")
        analysis["notifications"] = self.get_call_notifications(call_sid)
        
        if detailed:
            # Get additional detailed information
            logger.info("Fetching call feedback...")
            analysis["feedback"] = self.get_call_feedback(call_sid)
            
            logger.info("Fetching call summary...")
            analysis["summary"] = self.get_call_summary(call_sid)
            
            logger.info("Fetching SIP information...")
            analysis["sip_info"] = self.get_sip_logs(call_sid)
        
        return analysis

    def print_analysis(self, analysis: dict):
        """Print formatted analysis"""
        print("\n" + "="*80)
        print(f"TWILIO CALL ANALYSIS - {analysis['call_sid']}")
        print("="*80)
        
        # Call Details
        if analysis["call_details"]:
            details = analysis["call_details"]
            print(f"\n📞 CALL DETAILS:")
            print(f"   From: {details['from']}")
            print(f"   To: {details['to']}")
            print(f"   Status: {details['status']}")
            print(f"   Direction: {details['direction']}")
            print(f"   Duration: {details['duration']} seconds" if details['duration'] else "   Duration: N/A")
            print(f"   Price: {details['price']} {details['price_unit']}" if details['price'] else "   Price: N/A")
            print(f"   Start Time: {details['start_time']}")
            print(f"   End Time: {details['end_time']}")
            if details['trunk_sid']:
                print(f"   🚛 SIP Trunk: {details['trunk_sid']}")
            if details['answered_by']:
                print(f"   Answered By: {details['answered_by']}")
        
        # Events Timeline
        if analysis["events"]:
            print(f"\n⏰ CALL EVENTS ({len(analysis['events'])} events):")
            for event in analysis["events"]:
                print(f"   {event['timestamp']} - {event['event_type']}")
                if event['data']:
                    print(f"      Data: {event['data']}")
        
        # Notifications/Errors
        if analysis["notifications"]:
            print(f"\n🚨 NOTIFICATIONS/ERRORS ({len(analysis['notifications'])} notifications):")
            for notif in analysis["notifications"]:
                print(f"   Error Code: {notif['error_code']}")
                print(f"   Message: {notif['message_text']}")
                print(f"   Time: {notif['message_date']}")
                if notif['request_url']:
                    print(f"   Request URL: {notif['request_url']}")
                print()
        
        # Recordings
        if analysis["recordings"]:
            print(f"\n🎙️  RECORDINGS ({len(analysis['recordings'])} recordings):")
            for rec in analysis["recordings"]:
                print(f"   SID: {rec['sid']}")
                print(f"   Duration: {rec['duration']} seconds")
                print(f"   Status: {rec['status']}")
                print(f"   URI: {rec['uri']}")
                print()
        
        # Summary (if detailed)
        if analysis["summary"]:
            summary = analysis["summary"]
            print(f"\n📊 CALL SUMMARY:")
            print(f"   Call Type: {summary['call_type']}")
            print(f"   Call State: {summary['call_state']}")
            print(f"   Processing State: {summary['processing_state']}")
            if summary['quality_issues']:
                print(f"   Quality Issues: {summary['quality_issues']}")
            if summary['carrier']:
                print(f"   Carrier: {summary['carrier']}")
        
        # Feedback (if detailed)
        if analysis["feedback"]:
            feedback = analysis["feedback"]
            print(f"\n⭐ CALL FEEDBACK:")
            print(f"   Quality Score: {feedback['quality_score']}")
            if feedback['issues']:
                print(f"   Issues: {feedback['issues']}")

def main():
    parser = argparse.ArgumentParser(description='Analyze Twilio call logs')
    parser.add_argument('--call-sid', required=True, help='Twilio Call SID (e.g., CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx)')
    parser.add_argument('--detailed', action='store_true', help='Include detailed analysis (feedback, summary)')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--output', help='Save to file')
    
    args = parser.parse_args()
    
    # Validate Call SID format
    if not args.call_sid.startswith('CA') or len(args.call_sid) != 34:
        logger.error("Invalid Call SID format. Should be CAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
        return 1
    
    try:
        analyzer = TwilioCallAnalyzer()
        analysis = analyzer.analyze_call(args.call_sid, args.detailed)
        
        if args.json:
            output = json.dumps(analysis, indent=2, default=str)
            print(output)
        else:
            analyzer.print_analysis(analysis)
        
        # Save to file if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"Analysis saved to {args.output}")
        
        return 0
        
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Analysis failed: {e}")
        return 1

if __name__ == "__main__":
    exit(main())