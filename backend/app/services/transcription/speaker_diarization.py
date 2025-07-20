from typing import List, Dict, Optional
import re

class SpeakerDiarizationService:
    """
    Simple rule-based speaker diarization for counseling sessions
    In a real implementation, you might use pyannote.audio or similar
    """
    
    def __init__(self):
        # Keywords that might indicate counselor speech
        self.counselor_keywords = [
            "どのような", "お聞かせ", "いかがですか", "どう思われますか",
            "なるほど", "そうですね", "理解しました", "おっしゃる通り",
            "今日は", "お疲れ様", "ありがとうございます", "失礼いたします"
        ]
        
        # Keywords that might indicate client speech
        self.client_keywords = [
            "実は", "困っています", "悩んでいます", "どうしたらいいか",
            "わからない", "つらい", "悲しい", "嬉しい", "ありがとう"
        ]

    def assign_speakers(self, segments: List[Dict]) -> List[Dict]:
        """
        Assign speakers to transcription segments
        Returns segments with speaker labels ("counselor" or "client")
        """
        if not segments:
            return segments
        
        # Enhanced segments with speaker information
        enhanced_segments = []
        previous_speaker = None
        
        for i, segment in enumerate(segments):
            text = segment.get("text", "").lower()
            
            # Rule-based speaker detection
            speaker = self._detect_speaker(text, previous_speaker, i == 0)
            
            enhanced_segment = segment.copy()
            enhanced_segment["speaker"] = speaker
            enhanced_segment["speaker_confidence"] = self._calculate_confidence(text, speaker)
            
            enhanced_segments.append(enhanced_segment)
            previous_speaker = speaker
        
        # Post-process to smooth speaker transitions
        return self._smooth_speaker_transitions(enhanced_segments)

    def _detect_speaker(self, text: str, previous_speaker: Optional[str], is_first: bool) -> str:
        """
        Detect speaker based on text content and context
        """
        counselor_score = 0
        client_score = 0
        
        # Check for counselor keywords
        for keyword in self.counselor_keywords:
            if keyword in text:
                counselor_score += 2
        
        # Check for client keywords
        for keyword in self.client_keywords:
            if keyword in text:
                client_score += 2
        
        # Additional rules
        if re.search(r'[。！？].*ですか[。！？]?', text):  # Questions
            counselor_score += 1
        
        if re.search(r'ので|から|ため', text):  # Explanatory patterns
            client_score += 1
        
        # If first segment or no clear indicator, use heuristics
        if counselor_score == client_score:
            if is_first:
                return "counselor"  # Sessions often start with counselor
            elif previous_speaker:
                # Alternate speakers if no clear indication
                return "client" if previous_speaker == "counselor" else "counselor"
            else:
                return "counselor"
        
        return "counselor" if counselor_score > client_score else "client"

    def _calculate_confidence(self, text: str, assigned_speaker: str) -> float:
        """
        Calculate confidence score for speaker assignment
        """
        base_confidence = 0.5
        
        if assigned_speaker == "counselor":
            keywords = self.counselor_keywords
        else:
            keywords = self.client_keywords
        
        keyword_matches = sum(1 for keyword in keywords if keyword in text.lower())
        
        # Increase confidence based on keyword matches
        confidence = min(0.9, base_confidence + (keyword_matches * 0.1))
        
        return confidence

    def _smooth_speaker_transitions(self, segments: List[Dict]) -> List[Dict]:
        """
        Smooth out rapid speaker changes that are likely errors
        """
        if len(segments) < 3:
            return segments
        
        smoothed = segments.copy()
        
        for i in range(1, len(smoothed) - 1):
            current = smoothed[i]
            prev_speaker = smoothed[i-1]["speaker"]
            next_speaker = smoothed[i+1]["speaker"]
            
            # If current segment is different from both neighbors and has low confidence
            if (current["speaker"] != prev_speaker and 
                current["speaker"] != next_speaker and
                current.get("speaker_confidence", 0) < 0.7):
                
                # Check segment duration - if very short, likely an error
                duration = current.get("end", 0) - current.get("start", 0)
                if duration < 2:  # Less than 2 seconds
                    current["speaker"] = prev_speaker
                    current["speaker_confidence"] = 0.6
        
        return smoothed

    def get_speaker_statistics(self, segments: List[Dict]) -> Dict:
        """
        Calculate speaking time statistics for each speaker
        """
        stats = {
            "counselor": {"total_time": 0, "segment_count": 0},
            "client": {"total_time": 0, "segment_count": 0}
        }
        
        for segment in segments:
            speaker = segment.get("speaker", "unknown")
            if speaker in stats:
                duration = segment.get("end", 0) - segment.get("start", 0)
                stats[speaker]["total_time"] += duration
                stats[speaker]["segment_count"] += 1
        
        # Calculate percentages
        total_time = sum(s["total_time"] for s in stats.values())
        if total_time > 0:
            for speaker_stats in stats.values():
                speaker_stats["percentage"] = (speaker_stats["total_time"] / total_time) * 100
        
        return stats

speaker_diarization_service = SpeakerDiarizationService()