import mac_signing_buddy

from pathlib import Path


class SignAndNotarize:

    def __init__(self, path: Path, signing_identity: str, notarization_apple_id: str, notarization_password: str, notarization_team_id: str, entitlements: str = None) -> None:
        """
        Initialize
        """
        self._path = path
        self._signing_identity = signing_identity
        self._notarization_apple_id = notarization_apple_id
        self._notarization_password = notarization_password
        self._notarization_team_id = notarization_team_id
        self._entitlements = entitlements


    def sign_and_notarize(self) -> None:
        """
        Sign and Notarize
        """
        if not all([self._signing_identity, self._notarization_apple_id, self._notarization_password, self._notarization_team_id]):
            print("Signing and Notarization details not provided, skipping")
            return

        print(f"Signing {self._path.name}")
        mac_signing_buddy.Sign(
            identity=self._signing_identity,
            file=self._path,
            **({"entitlements": self._entitlements} if self._entitlements else {}),
        ).sign()

        print(f"Notarizing {self._path.name}")
        mac_signing_buddy.Notarize(
            apple_id=self._notarization_apple_id,
            password=self._notarization_password,
            team_id=self._notarization_team_id,
            file=self._path,
        ).sign()
