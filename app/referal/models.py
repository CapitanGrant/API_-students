from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, relationship, mapped_column
from app.database import Base, int_pk, str_uniq
from datetime import date



class ReferralCode(Base):
    id: Mapped[int_pk]
    code: Mapped[str_uniq]
    life_time: Mapped[date] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(nullable=False)

    #  Определяем отношения: один реферал может иметь один реферальный код
    referral: Mapped["Referral"] = relationship("Referral", back_populates="referral_code")

    extend_existing = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, code={self.code!r})"

    def __repr__(self):
        return str(self)

class Referral(Base):
    id: Mapped[int_pk]
    referral_code_id: Mapped[int] = mapped_column(ForeignKey("referralcodes.id"), nullable=True)
    referral_id: Mapped[int] = mapped_column(nullable=False)
    referrer_id: Mapped[int] = mapped_column(nullable=False)

    #  Определяем отношения: один реферрер может иметь множество рефералов
    referral_code: Mapped["ReferralCode"] = relationship("ReferralCode", back_populates="referral")
    user: Mapped["User"] = relationship("User", back_populates="referral")
    extend_existing = True

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, referral_id={self.referral_id!r})"

    def __repr__(self):
        return str(self)