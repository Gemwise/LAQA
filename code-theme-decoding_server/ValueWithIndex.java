public class ValueWithIndex {
    private final float qualityValue;
    private final int userIndex;

    public ValueWithIndex(float qualityValue, int userIndex) {
        this.qualityValue = qualityValue;
        this.userIndex = userIndex;
    }

    public float getValue() {
        return qualityValue;
    }

    public int getIndex() {
        return userIndex;
    }
}

