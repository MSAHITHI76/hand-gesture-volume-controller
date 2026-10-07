import math
import sys
import cv2
import numpy as np

# Windows system master volume control dependency
try:
    from comtypes import CLSCTX_ALL
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
    PYCAW_AVAILABLE = True
except ImportError:
    PYCAW_AVAILABLE = False

# MediaPipe hand tracking solution
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False


def init_windows_volume():
    """
    Initialize Windows System Master Volume Control interface using Pycaw.
    Supports modern Pycaw AudioDevice wrapper as well as classic COM interface.
    Returns:
        IAudioEndpointVolume object if successful, None otherwise.
    """
    if not PYCAW_AVAILABLE:
        print("[WARNING] Pycaw/Comtypes library not available. System volume control will be simulated.")
        return None
    try:
        devices = AudioUtilities.GetSpeakers()
        if hasattr(devices, "EndpointVolume"):
            return devices.EndpointVolume
        elif hasattr(devices, "Activate"):
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return interface.QueryInterface(IAudioEndpointVolume)
        elif hasattr(devices, "_dev") and hasattr(devices._dev, "Activate"):
            interface = devices._dev.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            return interface.QueryInterface(IAudioEndpointVolume)
        else:
            print("[WARNING] AudioUtilities.GetSpeakers() returned unrecognized device interface.")
            return None
    except Exception as e:
        print(f"[WARNING] Could not initialize Windows audio endpoint: {e}")
        return None


def calculate_distance(point1, point2):
    """
    Calculate Euclidean distance between two 2D points.
    """
    return math.hypot(point2[0] - point1[0], point2[1] - point1[1])


def map_distance_to_volume(distance, min_dist=25, max_dist=180):
    """
    Map hand landmark Euclidean distance (in pixels) to a normalized volume percentage [0.0, 100.0].
    Clamps output strictly within bounds.
    """
    if distance <= min_dist:
        return 0.0
    if distance >= max_dist:
        return 100.0
    
    normalized = ((distance - min_dist) / (max_dist - min_dist)) * 100.0
    return max(0.0, min(100.0, normalized))


def draw_ui(frame, volume_pct, hand_detected, thumb_pt=None, index_pt=None, distance=0.0):
    """
    Render visual feedback, volume bar, gesture distance line, and instructions on frame.
    """
    h, w, _ = frame.shape
    
    # 1. Title Box Overlay
    cv2.rectangle(frame, (15, 15), (460, 90), (20, 20, 20), cv2.FILLED)
    cv2.rectangle(frame, (15, 15), (460, 90), (0, 255, 200), 2)
    
    cv2.putText(frame, "HAND GESTURE VOLUME CONTROLLER", (25, 42),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2, cv2.LINE_AA)
    
    cv2.putText(frame, "Pinch/Spread Thumb & Index | Press 'Q' to Exit", (25, 72),
                cv2.FONT_HERSHEY_SIMPLEX, 0.45, (180, 180, 180), 1, cv2.LINE_AA)
    
    # 2. Hand Gesture Visualization
    if hand_detected and thumb_pt and index_pt:
        mid_x = (thumb_pt[0] + index_pt[0]) // 2
        mid_y = (thumb_pt[1] + index_pt[1]) // 2
        
        # Line connecting thumb tip and index finger tip
        cv2.line(frame, thumb_pt, index_pt, (255, 0, 128), 3)
        
        # Highlight tips and midpoint
        cv2.circle(frame, thumb_pt, 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, index_pt, 10, (0, 255, 0), cv2.FILLED)
        cv2.circle(frame, (mid_x, mid_y), 8, (0, 215, 255), cv2.FILLED)
        
        # Distance text tag
        cv2.putText(frame, f"{int(distance)} px", (mid_x + 15, mid_y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)
    else:
        # Hand missing status notification
        cv2.putText(frame, "Status: Searching for Hand...", (25, 125),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 140, 255), 2, cv2.LINE_AA)

    # 3. Visual Volume Bar
    bar_x1, bar_y1 = 35, 150
    bar_x2, bar_y2 = 70, 400
    
    # Outer bar container
    cv2.rectangle(frame, (bar_x1, bar_y1), (bar_x2, bar_y2), (255, 255, 255), 2)
    
    # Dynamic filled rectangle height
    fill_y = int(np.interp(volume_pct, [0, 100], [bar_y2, bar_y1]))
    
    # Color coding: Green/Teal for normal, Amber/Cyan for high
    if volume_pct > 80:
        bar_color = (0, 165, 255)
    elif volume_pct > 30:
        bar_color = (0, 255, 0)
    else:
        bar_color = (255, 180, 0)
        
    cv2.rectangle(frame, (bar_x1 + 2, fill_y), (bar_x2 - 2, bar_y2 - 2), bar_color, cv2.FILLED)
    
    # Volume percentage label
    cv2.putText(frame, f"Vol: {int(volume_pct)}%", (bar_x1 - 5, bar_y1 - 12),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)


def main():
    # Dependency check
    if not MEDIAPIPE_AVAILABLE:
        print("[ERROR] MediaPipe package is missing. Install requirements with: pip install -r requirements.txt")
        sys.exit(1)
        
    # Initialize Windows Master Volume Control
    vol_ctrl = init_windows_volume()
    current_vol = 50.0
    if vol_ctrl:
        try:
            current_vol = vol_ctrl.GetMasterVolumeLevelScalar() * 100.0
        except Exception:
            pass

    # Initialize MediaPipe Hands solution safely across MediaPipe versions
    try:
        if hasattr(mp, "solutions") and hasattr(mp.solutions, "hands"):
            mp_hands = mp.solutions.hands
            mp_drawing = mp.solutions.drawing_utils
            mp_styles = mp.solutions.drawing_styles
        else:
            import mediapipe.python.solutions.hands as mp_hands
            import mediapipe.python.solutions.drawing_utils as mp_drawing
            import mediapipe.python.solutions.drawing_styles as mp_styles
            
        hands = mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
    except Exception as err:
        print(f"[ERROR] Failed to initialize MediaPipe Hands: {err}")
        sys.exit(1)

    # Initialize Webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Could not open webcam device. Please check camera connection and permissions.")
        sys.exit(1)
        
    print("[INFO] Hand Gesture Volume Controller running. Press 'q' in the window to quit.")

    # Smoothing & Control parameters
    smoothed_vol = current_vol
    last_applied_vol = current_vol
    ALPHA = 0.25         # Exponential Moving Average smoothing factor
    DEAD_ZONE = 1.5      # Dead-zone volume delta threshold (%)
    MIN_DIST = 25        # Minimum pinch distance (pixels) -> 0% volume
    MAX_DIST = 180       # Maximum pinch distance (pixels) -> 100% volume

    try:
        while True:
            success, frame = cap.read()
            if not success or frame is None:
                print("[WARNING] Frame capture returned empty frame.")
                continue

            # Mirror frame horizontally for comfortable user experience
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape

            # Convert frame format from BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(rgb_frame)

            hand_detected = False
            thumb_pt = None
            index_pt = None
            raw_distance = 0.0

            if results.multi_hand_landmarks:
                hand_detected = True
                hand_landmarks = results.multi_hand_landmarks[0]
                
                # Draw skeleton landmarks
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_styles.get_default_hand_landmarks_style(),
                    mp_styles.get_default_hand_connections_style()
                )

                # Get Thumb Tip (Landmark 4) & Index Finger Tip (Landmark 8)
                thumb_lm = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
                index_lm = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

                thumb_pt = (int(thumb_lm.x * w), int(thumb_lm.y * h))
                index_pt = (int(index_lm.x * w), int(index_lm.y * h))

                # Calculate Euclidean landmark distance
                raw_distance = calculate_distance(thumb_pt, index_pt)

                # Map distance to target volume percentage
                target_vol = map_distance_to_volume(raw_distance, min_dist=MIN_DIST, max_dist=MAX_DIST)

                # Smooth volume using Exponential Moving Average
                smoothed_vol = (ALPHA * target_vol) + ((1.0 - ALPHA) * smoothed_vol)

                # Dead zone update control
                if abs(smoothed_vol - last_applied_vol) >= DEAD_ZONE:
                    last_applied_vol = smoothed_vol
                    if vol_ctrl:
                        try:
                            scalar_vol = max(0.0, min(1.0, smoothed_vol / 100.0))
                            vol_ctrl.SetMasterVolumeLevelScalar(scalar_vol, None)
                        except Exception as e:
                            print(f"[WARNING] Failed setting system volume: {e}")

            # Draw visual interface overlay
            draw_ui(frame, smoothed_vol, hand_detected, thumb_pt, index_pt, raw_distance)

            # Display window
            cv2.imshow("Hand Gesture Volume Controller", frame)

            # Exit cleanly when 'q' is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    except KeyboardInterrupt:
        print("[INFO] Session interrupted by user.")
    finally:
        # Resource cleanup
        hands.close()
        cap.release()
        cv2.destroyAllWindows()
        print("[INFO] Cleanup complete. Exited gracefully.")


if __name__ == "__main__":
    main()
